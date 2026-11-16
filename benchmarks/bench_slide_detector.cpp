// Throughput benchmark for ai_interview::SlideDetector::process_video().
//
// Renders a synthetic lecture video (slides + a small moving "webcam" box,
// a new slide every 60 frames) into a lossless FFV1/AVI file, then times
//   (1) decode only (cv::VideoCapture read loop), and
//   (2) SlideDetector::process_video() (decode + edge map + diff).
// Reports frames/s for each (median of N runs, single process).
//
// Usage: bench_slide_detector [width height frames runs]
//        defaults: 1280 720 300 5

#include <algorithm>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <string>
#include <vector>

#include <opencv2/opencv.hpp>

#include "ai_interview/slide_detector.hpp"

static cv::Mat make_slide(cv::Size size, int variant)
{
    cv::Mat img(size, CV_8UC3, cv::Scalar(255, 255, 255));
    cv::rectangle(img, cv::Rect(size.width / 32, size.height / 18, size.width * 15 / 16, size.height / 8),
                  cv::Scalar(0, 0, 0), cv::FILLED);
    for (int i = 0; i < 6; ++i)
    {
        int shift = (variant * 37 + i * 53) % (size.width / 4);
        cv::putText(img, "Slide " + std::to_string(variant) + " line " + std::to_string(i),
                    cv::Point(size.width / 16 + shift, size.height / 4 + i * size.height / 9),
                    cv::FONT_HERSHEY_SIMPLEX, size.height / 450.0, cv::Scalar(0, 0, 0), 2);
    }
    cv::rectangle(img, cv::Rect(size.width * (variant % 3 + 1) / 5, size.height / 2, size.width / 5, size.height / 3),
                  cv::Scalar(40, 40, 40), cv::FILLED);
    return img;
}

static double median(std::vector<double> v)
{
    std::sort(v.begin(), v.end());
    return v[v.size() / 2];
}

int main(int argc, char **argv)
{
    int w = argc > 1 ? std::atoi(argv[1]) : 1280;
    int h = argc > 2 ? std::atoi(argv[2]) : 720;
    int n = argc > 3 ? std::atoi(argv[3]) : 300;
    int runs = argc > 4 ? std::atoi(argv[4]) : 5;
    const cv::Size size(w, h);

    std::string path = (std::filesystem::temp_directory_path() / "bench_slide_detector.avi").string();
    {
        cv::VideoWriter wr(path, cv::VideoWriter::fourcc('F', 'F', 'V', '1'), 30.0, size);
        if (!wr.isOpened())
        {
            std::fprintf(stderr, "cannot open FFV1 writer\n");
            return 1;
        }
        cv::Mat slide;
        for (int i = 0; i < n; ++i)
        {
            if (i % 60 == 0)
                slide = make_slide(size, i / 60);
            cv::Mat f = slide.clone();
            int x = (i * 7) % (w - w / 8);
            cv::rectangle(f, cv::Rect(x, h - h / 8, w / 8, h / 8), cv::Scalar(120, 120, 120), cv::FILLED);
            wr.write(f);
        }
    }

    using clk = std::chrono::steady_clock;
    std::vector<double> decode_fps, detect_fps;
    size_t segments = 0;
    for (int r = 0; r < runs + 1; ++r) // first iteration is a warm-up
    {
        auto t0 = clk::now();
        cv::VideoCapture cap(path);
        cv::Mat f;
        int cnt = 0;
        while (cap.read(f))
            ++cnt;
        double dt = std::chrono::duration<double>(clk::now() - t0).count();
        if (r > 0)
            decode_fps.push_back(cnt / dt);

        ai_interview::SlideDetector det;
        t0 = clk::now();
        auto segs = det.process_video(path);
        dt = std::chrono::duration<double>(clk::now() - t0).count();
        segments = segs.size();
        if (r > 0)
            detect_fps.push_back(n / dt);
    }
    std::filesystem::remove(path);

    std::printf("resolution=%dx%d frames=%d runs=%d slides_detected=%zu\n", w, h, n, runs, segments);
    std::printf("decode_only_fps=%.1f\n", median(decode_fps));
    std::printf("process_video_fps=%.1f\n", median(detect_fps));
    return 0;
}

// Unit tests for ai_interview::SlideDetector.
//
// SlideDetector works on video files, so each test renders a short synthetic
// "presentation" (white slides with rectangles and text) into a temporary
// lossless FFV1/AVI file (so codec noise cannot
// influence the change metric) and runs process_video() on it.

#include <gtest/gtest.h>
#include <opencv2/opencv.hpp>

#include <cstdio>
#include <filesystem>
#include <random>
#include <string>
#include <vector>

#include "ai_interview/slide_detector.hpp"

namespace
{
    constexpr double kFps = 10.0;

    // Slide A: title bar, three text lines, picture placeholder on the right.
    cv::Mat make_slide_a(cv::Size size)
    {
        cv::Mat img(size, CV_8UC3, cv::Scalar(255, 255, 255));
        const double sx = size.width / 640.0, sy = size.height / 360.0;
        auto R = [&](int x, int y, int w, int h)
        { return cv::Rect(int(x * sx), int(y * sy), int(w * sx), int(h * sy)); };
        cv::rectangle(img, R(20, 20, 600, 50), cv::Scalar(0, 0, 0), cv::FILLED);
        for (int i = 0; i < 3; ++i)
            cv::putText(img, "Agenda item number " + std::to_string(i + 1),
                        cv::Point(int(30 * sx), int((120 + i * 50) * sy)),
                        cv::FONT_HERSHEY_SIMPLEX, 0.9 * sx, cv::Scalar(0, 0, 0), 2);
        cv::rectangle(img, R(400, 100, 200, 220), cv::Scalar(30, 30, 30), cv::FILLED);
        return img;
    }

    // Slide B: completely different layout (left block, bottom bar, big text).
    cv::Mat make_slide_b(cv::Size size)
    {
        cv::Mat img(size, CV_8UC3, cv::Scalar(255, 255, 255));
        const double sx = size.width / 640.0, sy = size.height / 360.0;
        auto R = [&](int x, int y, int w, int h)
        { return cv::Rect(int(x * sx), int(y * sy), int(w * sx), int(h * sy)); };
        cv::rectangle(img, R(20, 20, 250, 250), cv::Scalar(0, 0, 0), cv::FILLED);
        cv::rectangle(img, R(20, 300, 600, 40), cv::Scalar(0, 0, 0), cv::FILLED);
        cv::putText(img, "Results", cv::Point(int(300 * sx), int(120 * sy)),
                    cv::FONT_HERSHEY_SIMPLEX, 2.0 * sx, cv::Scalar(0, 0, 0), 4);
        cv::rectangle(img, R(300, 160, 300, 100), cv::Scalar(0, 0, 0), 3);
        return img;
    }

    // Slide A plus a small "webcam" box that covers ~1% of the frame.
    cv::Mat make_slide_a_with_small_box(cv::Size size)
    {
        cv::Mat img = make_slide_a(size);
        const double sx = size.width / 640.0, sy = size.height / 360.0;
        cv::rectangle(img, cv::Rect(int(40 * sx), int(280 * sy), int(64 * sx), int(36 * sy)),
                      cv::Scalar(0, 0, 0), cv::FILLED);
        return img;
    }

    struct Clip
    {
        cv::Mat frame;
        int frames; // how many consecutive frames to emit
    };

    // RAII temp video file.
    class TempVideo
    {
    public:
        TempVideo(const std::vector<Clip> &clips, cv::Size size)
        {
            // Random suffix: ctest may run test processes in parallel.
            std::random_device rd;
            path_ = (std::filesystem::temp_directory_path() /
                     ("slide_detector_test_" + std::to_string(rd()) + ".avi"))
                        .string();
            cv::VideoWriter w(path_, cv::VideoWriter::fourcc('F', 'F', 'V', '1'), kFps, size);
            ok_ = w.isOpened();
            if (!ok_)
                return;
            for (const auto &c : clips)
                for (int i = 0; i < c.frames; ++i)
                    w.write(c.frame);
        }
        ~TempVideo() { std::remove(path_.c_str()); }
        bool ok() const { return ok_; }
        const std::string &path() const { return path_; }

    private:
        std::string path_;
        bool ok_ = false;
    };

    const cv::Size kSize(640, 360);

#define MAKE_VIDEO_OR_SKIP(var, clips, size)                                 \
    TempVideo var(clips, size);                                              \
    if (!var.ok())                                                           \
        GTEST_SKIP() << "OpenCV build cannot write FFV1/AVI test videos";
} // namespace

using ai_interview::SlideDetector;

TEST(SlideDetector, StaticVideoYieldsOnlyFirstSegment)
{
    MAKE_VIDEO_OR_SKIP(video, (std::vector<Clip>{{make_slide_a(kSize), 60}}), kSize);
    SlideDetector det;
    auto segs = det.process_video(video.path());
    ASSERT_EQ(segs.size(), 1u);
    EXPECT_EQ(segs[0].frame_index, 0);
    EXPECT_DOUBLE_EQ(segs[0].timestamp_sec, 0.0);
    EXPECT_DOUBLE_EQ(segs[0].change_ratio, 1.0);
}

TEST(SlideDetector, DetectsSlideChange)
{
    MAKE_VIDEO_OR_SKIP(video,
                       (std::vector<Clip>{{make_slide_a(kSize), 30}, {make_slide_b(kSize), 30}}), kSize);
    SlideDetector det;
    auto segs = det.process_video(video.path());
    ASSERT_EQ(segs.size(), 2u);
    EXPECT_EQ(segs[0].frame_index, 0);
    EXPECT_EQ(segs[1].frame_index, 30);
    EXPECT_NEAR(segs[1].timestamp_sec, 3.0, 1e-9);
    EXPECT_GT(segs[1].change_ratio, ai_interview::DEFAULT_MIN_AREA_RATIO);
    EXPECT_LE(segs[1].change_ratio, 1.0);
}

TEST(SlideDetector, ReturningToPreviousSlideIsANewSegment)
{
    // A -> B -> A: each switch is compared with the last saved slide.
    MAKE_VIDEO_OR_SKIP(video,
                       (std::vector<Clip>{{make_slide_a(kSize), 30}, {make_slide_b(kSize), 30}, {make_slide_a(kSize), 30}}),
                       kSize);
    SlideDetector det;
    auto segs = det.process_video(video.path());
    ASSERT_EQ(segs.size(), 3u);
    EXPECT_EQ(segs[1].frame_index, 30);
    EXPECT_EQ(segs[2].frame_index, 60);
}

TEST(SlideDetector, MinSceneDurationDelaysDetection)
{
    // Slide changes at 1.0 s (frame 10) but min duration is 2.0 s, so the
    // change is only reported once 2.0 s have passed since the first slide.
    std::vector<Clip> clips{{make_slide_a(kSize), 10}, {make_slide_b(kSize), 40}};
    MAKE_VIDEO_OR_SKIP(video, clips, kSize);

    SlideDetector debounced(2.0, 0.20);
    auto segs = debounced.process_video(video.path());
    ASSERT_EQ(segs.size(), 2u);
    EXPECT_EQ(segs[1].frame_index, 20);

    SlideDetector immediate(0.0, 0.20);
    segs = immediate.process_video(video.path());
    ASSERT_EQ(segs.size(), 2u);
    EXPECT_EQ(segs[1].frame_index, 10);
}

TEST(SlideDetector, SmallChangeIgnoredAboveAreaThreshold)
{
    // A ~1% area change (webcam-sized box appears) must be treated as noise
    // with the default 20% threshold ...
    std::vector<Clip> clips{{make_slide_a(kSize), 30}, {make_slide_a_with_small_box(kSize), 30}};
    MAKE_VIDEO_OR_SKIP(video, clips, kSize);

    SlideDetector det(2.0, 0.20);
    EXPECT_EQ(det.process_video(video.path()).size(), 1u);

    // ... but is reported when the threshold is lowered below the change.
    SlideDetector sensitive(2.0, 0.005);
    auto segs = sensitive.process_video(video.path());
    ASSERT_EQ(segs.size(), 2u);
    EXPECT_EQ(segs[1].frame_index, 30);
    EXPECT_GT(segs[1].change_ratio, 0.005);
    EXPECT_LT(segs[1].change_ratio, 0.20);
}

TEST(SlideDetector, ThresholdOfOneNeverTriggers)
{
    // change_ratio is capped at 1.0 and the comparison is strict (>), so a
    // threshold of 1.0 can only ever yield the first segment.
    std::vector<Clip> clips{{make_slide_a(kSize), 30}, {make_slide_b(kSize), 30}};
    MAKE_VIDEO_OR_SKIP(video, clips, kSize);
    SlideDetector det(2.0, 1.0);
    EXPECT_EQ(det.process_video(video.path()).size(), 1u);
}

TEST(SlideDetector, ThresholdOfZeroStillIgnoresIdenticalFrames)
{
    // With threshold 0 any non-empty edge difference counts, but identical
    // frames (lossless video) produce identical edge maps: still 1 segment.
    MAKE_VIDEO_OR_SKIP(video, (std::vector<Clip>{{make_slide_a(kSize), 40}}), kSize);
    SlideDetector det(0.0, 0.0);
    EXPECT_EQ(det.process_video(video.path()).size(), 1u);
}

TEST(SlideDetector, LargeFramesAreDownscaledAndStillDetected)
{
    const cv::Size hd(1920, 1080); // wider than DEFAULT_RESIZE_WIDTH -> resize path
    std::vector<Clip> clips{{make_slide_a(hd), 25}, {make_slide_b(hd), 25}};
    MAKE_VIDEO_OR_SKIP(video, clips, hd);
    SlideDetector det;
    auto segs = det.process_video(video.path());
    ASSERT_EQ(segs.size(), 2u);
    EXPECT_EQ(segs[1].frame_index, 25);
}

TEST(SlideDetector, GetFrameReturnsRequestedFrame)
{
    std::vector<Clip> clips{{make_slide_a(kSize), 5}, {make_slide_b(kSize), 5}};
    MAKE_VIDEO_OR_SKIP(video, clips, kSize);
    SlideDetector det;
    cv::Mat a = det.get_frame(video.path(), 2);
    cv::Mat b = det.get_frame(video.path(), 7);
    ASSERT_FALSE(a.empty());
    ASSERT_FALSE(b.empty());
    EXPECT_EQ(b.size(), kSize);
    EXPECT_GT(cv::norm(a, b, cv::NORM_L1), 0.0); // frames 2 and 7 show different slides
    // Slide B has a solid black block at (20..270, 20..270).
    EXPECT_LT(cv::mean(b(cv::Rect(100, 100, 50, 50)))[0], 5.0);
}

TEST(SlideDetector, MissingVideoThrows)
{
    SlideDetector det;
    EXPECT_THROW(det.process_video("/nonexistent/path/video.mp4"), std::runtime_error);
    EXPECT_THROW(det.get_frame("/nonexistent/path/video.mp4", 0), std::runtime_error);
}

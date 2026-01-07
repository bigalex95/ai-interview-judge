#include "ai_interview/slide_detector.hpp"
#include <iostream>
#include <stdexcept>

namespace ai_interview
{

    SlideDetector::SlideDetector(double min_scene_duration_sec, double min_area_ratio)
        : min_duration_(min_scene_duration_sec),
          min_area_ratio_(min_area_ratio),
          frame_width_(0),
          frame_height_(0)
    {
    }

    cv::Mat SlideDetector::compute_edge_map(const cv::Mat &frame)
    {
        cv::Mat gray, blurred, edges, dilated;

        // 1. Convert to grayscale (color is not important for slide structure)
        cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);

        // 2. Blur noise (Gaussian Blur).
        // This is critical so that video compression artifacts are not counted as "edges".
        cv::GaussianBlur(gray, blurred, cv::Size(GAUSSIAN_BLUR_SIZE, GAUSSIAN_BLUR_SIZE), 0);

        // 3. Edge detection (Canny).
        // Leaves only sharp transitions (text, image frames).
        // The speaker's face has smooth transitions and will almost disappear.
        cv::Canny(blurred, edges, CANNY_THRESHOLD_LOW, CANNY_THRESHOLD_HIGH);

        // 4. Dilation.
        // Make lines thicker. This is needed so that small text shake
        // (by 1-2 pixels) doesn't produce huge difference when subtracting.
        cv::Mat kernel = cv::getStructuringElement(cv::MORPH_RECT,
                                                   cv::Size(DILATION_KERNEL_SIZE, DILATION_KERNEL_SIZE));
        cv::dilate(edges, dilated, kernel);

        return dilated;
    }

    double SlideDetector::calculate_change_metric(const cv::Mat &edges1, const cv::Mat &edges2)
    {
        if (edges1.empty() || edges2.empty())
            return 1.0;

        cv::Mat diff;
        // Calculate absolute difference between edge maps
        cv::absdiff(edges1, edges2, diff);

        // Find contours of changes
        std::vector<std::vector<cv::Point>> contours;
        cv::findContours(diff, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);

        double total_change_area = 0.0;
        double frame_area = (double)(diff.rows * diff.cols);

        for (const auto &contour : contours)
        {
            // Get bounding rectangle of the change
            cv::Rect rect = cv::boundingRect(contour);
            total_change_area += rect.area();
        }

        // Return fraction of changed area (0.0 - 1.0)
        return total_change_area / frame_area;
    }

    std::vector<SlideSegment> SlideDetector::process_video(const std::string &video_path)
    {
        cv::VideoCapture cap(video_path);
        if (!cap.isOpened())
        {
            throw std::runtime_error("Could not open video: " + video_path);
        }

        frame_width_ = (int)cap.get(cv::CAP_PROP_FRAME_WIDTH);
        frame_height_ = (int)cap.get(cv::CAP_PROP_FRAME_HEIGHT);
        double fps = cap.get(cv::CAP_PROP_FPS);

        std::vector<SlideSegment> segments;
        cv::Mat last_saved_edges; // Store edges of the last saved slide
        cv::Mat frame;

        int frame_idx = 0;
        double last_slide_time = -min_duration_; // So the first frame can become a slide

        while (cap.read(frame))
        {
            // Optimization: process not every frame, but for example every 5th,
            // if video is 30-60 fps. But for now we take every frame to keep it simple.

            // Get edge map of current frame
            // Resize for speed (process at 720p even if video is 4k)
            cv::Mat resized;
            float scale = 1.0;
            if (frame.cols > DEFAULT_RESIZE_WIDTH)
            {
                scale = static_cast<float>(DEFAULT_RESIZE_WIDTH) / frame.cols;
                cv::resize(frame, resized, cv::Size(), scale, scale);
            }
            else
            {
                resized = frame;
            }

            cv::Mat current_edges = compute_edge_map(resized);
            double timestamp = frame_idx / fps;

            if (last_saved_edges.empty())
            {
                // Always consider the first frame as the beginning of the first slide
                segments.push_back({frame_idx, timestamp, 1.0});
                last_slide_time = timestamp;
                last_saved_edges = current_edges.clone(); // Remember as reference
            }
            else
            {
                // COMPARE WITH REFERENCE, NOT WITH PREVIOUS FRAME
                double change_score = calculate_change_metric(last_saved_edges, current_edges);

                // DETECTION LOGIC:
                // 1. Change is greater than threshold (min_area_ratio)
                // 2. Enough time has passed since last slide (min_duration)
                if (change_score > min_area_ratio_ && (timestamp - last_slide_time) >= min_duration_)
                {
                    segments.push_back({frame_idx, timestamp, change_score});
                    last_slide_time = timestamp;
                    last_saved_edges = current_edges.clone(); // Update reference only on slide change
                }
            }

            frame_idx++;
        }

        cap.release();
        return segments;
    }

    cv::Mat SlideDetector::get_frame(const std::string &video_path, int frame_index)
    {
        cv::VideoCapture cap(video_path);
        if (!cap.isOpened())
        {
            throw std::runtime_error("Could not open video: " + video_path);
        }

        // Jump directly to the needed frame (seek)
        cap.set(cv::CAP_PROP_POS_FRAMES, frame_index);

        cv::Mat frame;
        cap.read(frame);
        return frame; // Если кадр не считан, вернется пустой Mat, это ок
    }

} // namespace ai_interview
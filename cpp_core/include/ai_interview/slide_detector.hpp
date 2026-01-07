#pragma once

#include <opencv2/opencv.hpp>
#include <vector>
#include <string>

namespace ai_interview
{
    // Default configuration constants
    constexpr double DEFAULT_MIN_SCENE_DURATION = 2.0;
    constexpr double DEFAULT_MIN_AREA_RATIO = 0.20;
    constexpr int DEFAULT_RESIZE_WIDTH = 1280;
    constexpr int GAUSSIAN_BLUR_SIZE = 5;
    constexpr int CANNY_THRESHOLD_LOW = 50;
    constexpr int CANNY_THRESHOLD_HIGH = 150;
    constexpr int DILATION_KERNEL_SIZE = 3;

    /**
     * @brief Structure describing a detected slide.
     * We use a POD (Plain Old Data) structure so that pybind11
     * can easily convert it to a Python dict or object.
     */
    struct SlideSegment
    {
        int frame_index;      // Frame number where the slide appeared
        double timestamp_sec; // Timestamp in seconds
        double change_ratio;  // Screen change percentage (0.0 - 1.0) compared to previous slide
    };

    class SlideDetector
    {
    public:
        /**
         * @brief Constructor
         * @param min_scene_duration_sec Minimum time (seconds) between slide changes.
         * Protects against "flickering" (e.g., if speaker quickly returns to previous slide).
         * Defaults to 2.0 seconds.
         * @param min_area_ratio Change area threshold (0.0 - 1.0).
         * If less than this percentage of the screen changed, we consider it noise (or head movement).
         * If more than this percentage - it's a new slide. Defaults to 0.20 (20%).
         */
        SlideDetector(double min_scene_duration_sec = DEFAULT_MIN_SCENE_DURATION,
                      double min_area_ratio = DEFAULT_MIN_AREA_RATIO);

        // Default destructor
        ~SlideDetector() = default;

        /**
         * @brief Main video processing pipeline.
         * Reads video, searches for transitions, returns list of unique moments.
         * @param video_path Path to mp4 file.
         * @return std::vector<SlideSegment> List of metadata about slides.
         */
        std::vector<SlideSegment> process_video(const std::string &video_path);

        /**
         * @brief Helper for Python: extract a specific frame as an image.
         * We don't store all images in memory (that would kill RAM).
         * Python gets indices from process_video, then requests needed frames via this method.
         */
        cv::Mat get_frame(const std::string &video_path, int frame_index);

    private:
        double min_duration_;
        double min_area_ratio_;
        int frame_width_;
        int frame_height_;

        // Internal methods for logic (hidden from Python)

        // 1. Converts frame to B&W contours (Canny Edge Detection)
        cv::Mat compute_edge_map(const cv::Mat &frame);

        // 2. Compares two contour frames and returns percentage of changed area
        double calculate_change_metric(const cv::Mat &edges1, const cv::Mat &edges2);
    };

} // namespace ai_interview
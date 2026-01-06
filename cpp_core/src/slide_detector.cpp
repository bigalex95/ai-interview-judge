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

        // 1. Конвертируем в ЧБ (цвет не важен для структуры слайда)
        cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);

        // 2. Размываем шум (Gaussian Blur).
        // Это критично, чтобы артефакты сжатия видео не считались "границами".
        cv::GaussianBlur(gray, blurred, cv::Size(5, 5), 0);

        // 3. Детекция границ (Canny).
        // Оставляет только резкие переходы (текст, рамки картинок).
        // Лицо спикера имеет мягкие переходы и почти исчезнет.
        cv::Canny(blurred, edges, 50, 150);

        // 4. Расширение (Dilation).
        // Делаем линии жирнее. Это нужно, чтобы мелкая тряска текста
        // (на 1-2 пикселя) не давала огромную разницу при вычитании.
        cv::Mat kernel = cv::getStructuringElement(cv::MORPH_RECT, cv::Size(3, 3));
        cv::dilate(edges, dilated, kernel);

        return dilated;
    }

    double SlideDetector::calculate_change_metric(const cv::Mat &edges1, const cv::Mat &edges2)
    {
        if (edges1.empty() || edges2.empty())
            return 1.0;

        cv::Mat diff;
        // Считаем абсолютную разницу между картами границ
        cv::absdiff(edges1, edges2, diff);

        // Находим контуры изменений
        std::vector<std::vector<cv::Point>> contours;
        cv::findContours(diff, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);

        double total_change_area = 0.0;
        double frame_area = (double)(diff.rows * diff.cols);

        for (const auto &contour : contours)
        {
            // Берем ограничивающий прямоугольник изменения
            cv::Rect rect = cv::boundingRect(contour);
            total_change_area += rect.area();
        }

        // Возвращаем долю изменившейся площади (0.0 - 1.0)
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
        cv::Mat prev_edges;
        cv::Mat frame;

        int frame_idx = 0;
        double last_slide_time = -min_duration_; // Чтобы первый кадр мог стать слайдом

        while (cap.read(frame))
        {
            // Оптимизация: обрабатываем не каждый кадр, а например каждый 5-й,
            // если видео 30-60 fps. Но для начала берем каждый, чтобы не усложнять.

            // Получаем карту границ текущего кадра
            // Resize для ускорения (обрабатываем в 720p даже если видео 4k)
            cv::Mat resized;
            float scale = 1.0;
            if (frame.cols > 1280)
            {
                scale = 1280.0f / frame.cols;
                cv::resize(frame, resized, cv::Size(), scale, scale);
            }
            else
            {
                resized = frame;
            }

            cv::Mat current_edges = compute_edge_map(resized);
            double timestamp = frame_idx / fps;

            if (prev_edges.empty())
            {
                // Первый кадр всегда считаем началом первого слайда
                segments.push_back({frame_idx, timestamp, 1.0});
                last_slide_time = timestamp;
            }
            else
            {
                double change_score = calculate_change_metric(prev_edges, current_edges);

                // ЛОГИКА ДЕТЕКЦИИ:
                // 1. Изменение больше порога (min_area_ratio)
                // 2. Прошло достаточно времени с прошлого слайда (min_duration)
                if (change_score > min_area_ratio_ && (timestamp - last_slide_time) >= min_duration_)
                {
                    segments.push_back({frame_idx, timestamp, change_score});
                    last_slide_time = timestamp;
                }
            }

            prev_edges = current_edges.clone();
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

        // Прыгаем сразу к нужному кадру (seek)
        cap.set(cv::CAP_PROP_POS_FRAMES, frame_index);

        cv::Mat frame;
        cap.read(frame);
        return frame; // Если кадр не считан, вернется пустой Mat, это ок
    }

} // namespace ai_interview
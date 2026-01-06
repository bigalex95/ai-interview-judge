#pragma once

#include <opencv2/opencv.hpp>
#include <vector>
#include <string>

namespace ai_interview
{

    /**
     * @brief Структура, описывающая найденный слайд.
     * Мы используем POD (Plain Old Data) структуру, чтобы pybind11
     * легко превратил её в Python dict или объект.
     */
    struct SlideSegment
    {
        int frame_index;      // Номер кадра, где слайд появился
        double timestamp_sec; // Время в секундах
        double change_ratio;  // Процент изменения экрана (0.0 - 1.0) по сравнению с прошлым слайдом
    };

    class SlideDetector
    {
    public:
        /**
         * @brief Конструктор
         * @param min_scene_duration_sec Минимальное время (сек) между сменами слайдов.
         * Защищает от "мигания" (например, если спикер быстро вернул слайд назад).
         * @param min_area_ratio Порог площади изменений (0.0 - 1.0).
         * Если изменилось < 20% экрана, мы считаем это шумом (или движением головы).
         * Если > 20% - это новый слайд.
         */
        SlideDetector(double min_scene_duration_sec = 2.0, double min_area_ratio = 0.20);

        // Деструктор по умолчанию
        ~SlideDetector() = default;

        /**
         * @brief Основной пайплайн обработки видео.
         * Читает видео, ищет переходы, возвращает список уникальных моментов.
         * * @param video_path Путь к mp4 файлу.
         * @return std::vector<SlideSegment> Список метаданных о слайдах.
         */
        std::vector<SlideSegment> process_video(const std::string &video_path);

        /**
         * @brief Хелпер для Python: достать конкретный кадр как картинку.
         * Мы не храним все картинки в памяти (это убьет RAM).
         * Python получит индексы из process_video, а потом запросит нужные кадры через этот метод.
         */
        cv::Mat get_frame(const std::string &video_path, int frame_index);

    private:
        double min_duration_;
        double min_area_ratio_;
        int frame_width_;
        int frame_height_;

        // Внутренние методы для логики (скрыты от Python)

        // 1. Превращает кадр в ч/б контуры (Canny Edge Detection)
        cv::Mat compute_edge_map(const cv::Mat &frame);

        // 2. Сравнивает два кадра контуров и возвращает процент изменившейся площади
        double calculate_change_metric(const cv::Mat &edges1, const cv::Mat &edges2);
    };

} // namespace ai_interview
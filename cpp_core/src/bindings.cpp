#include <pybind11/pybind11.h>
#include <pybind11/stl.h>   // Для автоматической конвертации std::vector
#include <pybind11/numpy.h> // Для работы с numpy массивами
#include "ai_interview/slide_detector.hpp"

namespace py = pybind11;

// --- Вспомогательная функция для конвертации cv::Mat -> numpy array ---
// OpenCV хранит данные в BGR, Python обычно хочет RGB или тоже BGR.
// Мы вернем "как есть", Python сам разберется.
py::array_t<uint8_t> mat_to_numpy(const cv::Mat &mat)
{
    if (mat.empty())
    {
        return py::array_t<uint8_t>();
    }

    // Определяем форму массива (height, width, channels)
    std::vector<ssize_t> shape = {mat.rows, mat.cols};
    std::vector<ssize_t> strides = {mat.step[0], mat.step[1]};

    if (mat.channels() > 1)
    {
        shape.push_back(mat.channels());
        strides.push_back(mat.elemSize1());
    }

    // Создаем numpy array, который ссылается на данные Mat или копирует их
    // В данном случае безопаснее скопировать данные, чтобы Python владел памятью
    return py::array_t<uint8_t>(shape, strides, mat.data).attr("copy")();
}

// --- Определение модуля ---
PYBIND11_MODULE(ai_interview_cpp, m)
{
    m.doc() = "C++ backend for AI Interview Judge video processing";

    // 1. Биндим структуру SlideSegment
    py::class_<ai_interview::SlideSegment>(m, "SlideSegment")
        .def_readwrite("frame_index", &ai_interview::SlideSegment::frame_index)
        .def_readwrite("timestamp_sec", &ai_interview::SlideSegment::timestamp_sec)
        .def_readwrite("change_ratio", &ai_interview::SlideSegment::change_ratio)
        .def("__repr__", [](const ai_interview::SlideSegment &s)
             { return "<SlideSegment frame=" + std::to_string(s.frame_index) +
                      " time=" + std::to_string(s.timestamp_sec) + ">"; });

    // 2. Биндим класс SlideDetector
    py::class_<ai_interview::SlideDetector>(m, "SlideDetector")
        .def(py::init<double, double>(),
             py::arg("min_scene_duration_sec") = 2.0,
             py::arg("min_area_ratio") = 0.20)
        .def("process_video", &ai_interview::SlideDetector::process_video,
             "Scans video for slide transitions")
        .def("get_frame", [](ai_interview::SlideDetector &self, const std::string &path, int idx)
             {
            // Кастомная обертка для конвертации Mat -> Numpy
            cv::Mat frame = self.get_frame(path, idx);
            return mat_to_numpy(frame); }, "Get specific video frame as numpy array");
}
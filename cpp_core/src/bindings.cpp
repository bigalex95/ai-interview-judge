#include <pybind11/pybind11.h>
#include <pybind11/stl.h>   // For automatic std::vector conversion
#include <pybind11/numpy.h> // For working with numpy arrays
#include "ai_interview/slide_detector.hpp"

namespace py = pybind11;

// --- Helper function for converting cv::Mat -> numpy array ---
// OpenCV stores data in BGR, Python usually wants RGB or also BGR.
// We return "as is", Python will figure it out.
py::array_t<uint8_t> mat_to_numpy(const cv::Mat &mat)
{
    if (mat.empty())
    {
        return py::array_t<uint8_t>();
    }

    // Define array shape (height, width, channels)
    std::vector<ssize_t> shape = {mat.rows, mat.cols};
    std::vector<ssize_t> strides = {mat.step[0], mat.step[1]};

    if (mat.channels() > 1)
    {
        shape.push_back(mat.channels());
        strides.push_back(mat.elemSize1());
    }

    // Create numpy array that references Mat data or copies it
    // In this case it's safer to copy the data so Python owns the memory
    return py::array_t<uint8_t>(shape, strides, mat.data).attr("copy")();
}

// --- Module definition ---
PYBIND11_MODULE(ai_interview_cpp, m)
{
    m.doc() = "C++ backend for AI Interview Judge video processing";

    // 1. Bind SlideSegment structure
    py::class_<ai_interview::SlideSegment>(m, "SlideSegment")
        .def_readwrite("frame_index", &ai_interview::SlideSegment::frame_index)
        .def_readwrite("timestamp_sec", &ai_interview::SlideSegment::timestamp_sec)
        .def_readwrite("change_ratio", &ai_interview::SlideSegment::change_ratio)
        .def("__repr__", [](const ai_interview::SlideSegment &s)
             { return "<SlideSegment frame=" + std::to_string(s.frame_index) +
                      " time=" + std::to_string(s.timestamp_sec) + ">"; });

    // 2. Bind SlideDetector class
    py::class_<ai_interview::SlideDetector>(m, "SlideDetector")
        .def(py::init<double, double>(),
             py::arg("min_scene_duration_sec") = 2.0,
             py::arg("min_area_ratio") = 0.20)
        .def("process_video", &ai_interview::SlideDetector::process_video,
             "Scans video for slide transitions")
        .def("get_frame", [](ai_interview::SlideDetector &self, const std::string &path, int idx)
             {
            // Custom wrapper for converting Mat -> Numpy
            cv::Mat frame = self.get_frame(path, idx);
            return mat_to_numpy(frame); }, "Get specific video frame as numpy array");
}
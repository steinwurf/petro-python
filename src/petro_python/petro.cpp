// Copyright (c) Steinwurf ApS 2016.
// All Rights Reserved
//
// Distributed under the "BSD License". See the accompanying LICENSE.rst file.

#include <boost/python.hpp>

#include <cstdint>
#include <string>
#include <vector>
#include <system_error>

#include <petro/extractor/aac_sample_extractor.hpp>
#include <petro/extractor/avc_sample_extractor.hpp>

namespace petro_python
{

static PyObject* pointer_to_python(const uint8_t* data, uint32_t size)
{
#if PY_MAJOR_VERSION >= 3
    return PyBytes_FromStringAndSize((char*)data, size);
#else
    return PyString_FromStringAndSize((char*)data, size);
#endif
}

template<class Extractor>
void open(Extractor& extractor)
{
    std::error_code error;
    extractor.open(error);
    if (error)
    {
        throw std::system_error(error);
    }
}

template<class Extractor>
PyObject* sample_data(Extractor& extractor)
{
    return pointer_to_python(extractor.sample_data(), extractor.sample_size());
}

PyObject* adts_header(petro::extractor::aac_sample_extractor& extractor)
{
    std::vector<uint8_t> adts_header(extractor.adts_header_size());
    extractor.write_adts_header(adts_header.data());
    return pointer_to_python(adts_header.data(), adts_header.size());
}

PyObject* sps(petro::extractor::avc_sample_extractor& extractor)
{
    return pointer_to_python(extractor.sps_data(), extractor.sps_size());
}

PyObject* pps(petro::extractor::avc_sample_extractor& extractor)
{
    return pointer_to_python(extractor.pps_data(), extractor.pps_size());
}

template<class ExtractorClass>
void define_extractor_functions(ExtractorClass& extrator_class)
{
    using extractor_type = typename ExtractorClass::wrapped_type;
    using boost::python::arg;

    extrator_class
    .def("open", &open<extractor_type>,
         "Open extractor. Throws an exception if the operation was successful.")
    .def("close", &extractor_type::close, "Close extractor.")
    .def("reset", &extractor_type::reset, "Reset extractor.")
    .def("file_path", &extractor_type::file_path,
         "Return the file path.\n\n"
         "\t:returns: The file path.\n")
    .def("set_file_path", &extractor_type::set_file_path,
         arg("file_path"),
         "Set the file path of the fíle to open.\n\n"
         "\t:param file_path: The file path of the file to open.")
    .def("media_duration", &extractor_type::media_duration,
         "Return the total media duration in microseconds.\n\n"
         "\t:returns: The total media duration in microseconds.\n")
    .def("decoding_timestamp", &extractor_type::decoding_timestamp,
         "Return the decoding timestamp related to the current sample.\n\n"
         "\t:returns: The decoding timestamp related to the current sample.\n")
    .def("presentation_timestamp", &extractor_type::presentation_timestamp,
         "Return the presentation timestamp related to the current sample.\n\n"
         "\t:returns: The presentation timestamp related to the current "
         "sample.\n")
    .def("advance", &extractor_type::advance, "Advance extractor.")
    .def("at_end", &extractor_type::at_end,
         "Return true if no more sample are available.\n\n"
         "\t:returns: True if no more sample are available, otherwise False.\n")
    .def("sample_index", &extractor_type::sample_index,
         "Return the current sample index.\n\n"
         "\t:returns: The current sample index.\n")
    .def("sample_size", &extractor_type::sample_size,
         "Return the current sample size.\n\n"
         "\t:returns: The current sample size.\n")
    .def("sample_data", &sample_data<extractor_type>,
         "Return the current sample data.\n\n"
         "\t:returns: The current sample data.\n");
}

void create_extractors()
{
    using boost::python::class_;
    using boost::python::init;

    auto aac_extractor_class =
        class_<petro::extractor::aac_sample_extractor, boost::noncopyable>(
            "AACSampleExtractor",
            "Extractor for extracting AAC samples.",
            init<>("Extractor constructor."));
    define_extractor_functions(aac_extractor_class);
    aac_extractor_class
    .def("adts_header", &adts_header,
         "Return the current adts header.\n\n"
         "\t:returns: The current adts header.\n");

    auto avc_extractor_class =
        class_<petro::extractor::avc_sample_extractor, boost::noncopyable>(
            "AVCSampleExtractor",
            "Extractor for extracting AVC samples.",
            init<>("Extractor constructor."));
    define_extractor_functions(avc_extractor_class);
    avc_extractor_class
    .def("sps", &sps,
         "Return the sequence parameter set.\n\n"
         "\t:returns: The sequence parameter set.\n")
    .def("pps", &pps,
         "Return the picture parameter set.\n\n"
         "\t:returns: The picture parameter set.\n")
    .def("nalu_length_size",
         &petro::extractor::avc_sample_extractor::nalu_length_size,
         "Return the nalu length size.\n\n"
         "\t:returns: the size of the length preceeded each nalu sample in the "
         "h264 sample.\n");
}

std::string version()
{
    std::string version = std::string("petro-python: ");
    version += STEINWURF_PETRO_PYTHON_VERSION;

    // Add dependency versions:
    version += std::string("\n\tpetro: ");
#ifdef STEINWURF_PETRO_VERSION
    version += std::string(STEINWURF_PETRO_VERSION);
#endif
    version += std::string("\n\tboost: ");
#ifdef STEINWURF_BOOST_VERSION
    version += std::string(STEINWURF_BOOST_VERSION);
#endif

    return version;
}

void create_version_function()
{
    using namespace boost::python;
    scope().attr("__version__") = version();
}

BOOST_PYTHON_MODULE(petro)
{
    boost::python::docstring_options doc_options;
    doc_options.disable_signatures();
    create_version_function();
    create_extractors();
}
}

// Copyright (c) James Hilton-Balfe under the MIT License see LICENSE

#include <google/protobuf/compiler/command_line_interface.h>
#include <google/protobuf/compiler/importer.h>
#include <google/protobuf/descriptor.h>
#include <google/protobuf/io/tokenizer.h>

namespace compiler = google::protobuf::compiler;
namespace io = google::protobuf::io;

#pragma once
class Error {  // TODO make this inherit from Exception
   public:
    std::string filename;
    int line;
    int column;
    std::string message;
    bool warning;

    Error(const std::string& filename_,
          int line_,
          int column_,
          const std::string& message_,
          bool warning_) {
        filename = filename_;
        line = line_;
        column = column_;
        message = message_;
        warning = warning_;
    }
};

#pragma once
class ErrorCollector : public google::protobuf::DescriptorPool::ErrorCollector,
                       public io::ErrorCollector,
                       public compiler::MultiFileErrorCollector {
   public:
    std::vector<Error> errors;
    std::string current_filename;
    bool has_errors;  // doesn't have warnings

    // parsing errors
    void AddError(int line, int column, const std::string& message) override {
        errors.emplace_back(current_filename, line + 1, column + 1, message,
                            false);
        has_errors = true;
    }
    void AddWarning(int line, int column, const std::string& message) override {
        errors.emplace_back(current_filename, line + 1, column + 1, message,
                            true);
    }

    // conversion errors
    void AddError(const std::string& filename,
                  const std::string& element_name,
                  const google::protobuf::Message* descriptor,
                  ErrorLocation location,
                  const std::string& message) override {
        errors.emplace_back(filename, 1, 1, message, false);
        has_errors = true;
    }

    void AddWarning(const std::string& filename,
                    const std::string& element_name,
                    const google::protobuf::Message* descriptor,
                    ErrorLocation location,
                    const std::string& message) override {
        errors.emplace_back(filename, 1, 1, message, true);
    }

    void AddError(const std::string& filename,
                  int line,
                  int column,
                  const std::string& message) override {
        errors.emplace_back(filename, line, column, message, true);
    }

    void AddWarning(const std::string& filename,
                    int line,
                    int column,
                    const std::string& message) override {
        errors.emplace_back(filename, line, column, message, false);
    }

    ErrorCollector() {
        errors = std::vector<Error>();
        current_filename = std::string();
        has_errors = false;
    }
};
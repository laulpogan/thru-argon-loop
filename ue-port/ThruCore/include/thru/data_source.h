#pragma once

#include <string>
#include <memory>
#include <unordered_map>
#include <fstream>
#include <sstream>
#include <nlohmann/json.hpp>

namespace thru {

/**
 * Interface for loading game data tables and configuration.
 * Enables decoupling core systems from filesystem access and provides mock/memory sources for tests.
 */
class DataSource {
public:
    virtual ~DataSource() = default;

    virtual bool exists(const std::string& path) const = 0;
    virtual std::string read_string(const std::string& path) const = 0;
    virtual nlohmann::json read_json(const std::string& path) const = 0;
};

/**
 * Filesystem-backed DataSource.
 */
class FileDataSource : public DataSource {
public:
    explicit FileDataSource(std::string root_dir = "")
        : root_dir_(std::move(root_dir)) {}

    bool exists(const std::string& path) const override {
        const std::string full_path = resolve(path);
        std::ifstream f(full_path);
        return f.good();
    }

    std::string read_string(const std::string& path) const override {
        const std::string full_path = resolve(path);
        std::ifstream f(full_path);
        if (!f.is_open()) {
            return {};
        }
        std::stringstream ss;
        ss << f.rdbuf();
        return ss.str();
    }

    nlohmann::json read_json(const std::string& path) const override {
        const std::string str = read_string(path);
        if (str.empty()) {
            return nlohmann::json();
        }
        try {
            return nlohmann::json::parse(str);
        } catch (...) {
            return nlohmann::json();
        }
    }

private:
    std::string root_dir_;

    std::string resolve(const std::string& path) const {
        if (root_dir_.empty() || path.rfind('/', 0) == 0) {
            return path;
        }
        if (!root_dir_.empty() && root_dir_.back() == '/') {
            return root_dir_ + path;
        }
        return root_dir_ + "/" + path;
    }
};

/**
 * In-memory DataSource for unit testing without disk dependencies.
 */
class MemoryDataSource : public DataSource {
public:
    void put_string(const std::string& path, std::string content) {
        files_[path] = std::move(content);
    }

    void put_json(const std::string& path, const nlohmann::json& j) {
        files_[path] = j.dump();
    }

    bool exists(const std::string& path) const override {
        return files_.find(path) != files_.end();
    }

    std::string read_string(const std::string& path) const override {
        auto it = files_.find(path);
        if (it == files_.end()) {
            return {};
        }
        return it->second;
    }

    nlohmann::json read_json(const std::string& path) const override {
        auto it = files_.find(path);
        if (it == files_.end()) {
            return nlohmann::json();
        }
        try {
            return nlohmann::json::parse(it->second);
        } catch (...) {
            return nlohmann::json();
        }
    }

private:
    std::unordered_map<std::string, std::string> files_;
};

} // namespace thru

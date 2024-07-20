#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include <dirent.h>

// 日志记录
void log_message(const char *message) {
    FILE *log_file = fopen("quarantine.log", "a");
    if (log_file) {
        fprintf(log_file, "%s\n", message);
        fclose(log_file);
    }
}

// 加载文件名列表
int load_file_list(const char *file_list_path, char ***file_list, int *count) {
    FILE *file = fopen(file_list_path, "r");
    if (!file) return -1;

    char line[256];
    *count = 0;
    *file_list = NULL;

    while (fgets(line, sizeof(line), file)) {
        (*count)++;
        *file_list = realloc(*file_list, sizeof(char *) * (*count));
        line[strcspn(line, "\n")] = 0;
        (*file_list)[(*count) - 1] = strdup(line);
    }

    fclose(file);
    return 0;
}

// 保存文件名列表
int save_file_list(const char *file_list_path, char **file_list, int count) {
    FILE *file = fopen(file_list_path, "w");
    if (!file) return -1;

    for (int i = 0; i < count; i++) {
        fprintf(file, "%s\n", file_list[i]);
    }

    fclose(file);
    return 0;
}

// 移动文件
int move_file(const char *src, const char *dst) {
    if (rename(src, dst) != 0) {
        perror("Error moving file");
        return -1;
    }
    return 0;
}

// 隔离文件
void isolate_files(const char *source_dir, const char *quarantine_dir, char **file_list, int file_count) {
    DIR *dir;
    struct dirent *ent;

    if ((dir = opendir(source_dir)) != NULL) {
        while ((ent = readdir(dir)) != NULL) {
            if (ent->d_type == DT_REG) {
                int found = 0;
                for (int i = 0; i < file_count; i++) {
                    if (strcmp(ent->d_name, file_list[i]) == 0) {
                        found = 1;
                        break;
                    }
                }

                if (!found) {
                    char src_path[512], dst_path[512];
                    snprintf(src_path, sizeof(src_path), "%s/%s", source_dir, ent->d_name);
                    snprintf(dst_path, sizeof(dst_path), "%s/%s", quarantine_dir, ent->d_name);
                    if (move_file(src_path, dst_path) == 0) {
                        char log_msg[512];
                        snprintf(log_msg, sizeof(log_msg), "Moved: %s to %s", src_path, dst_path);
                        log_message(log_msg);
                    }
                }
            }
        }
        closedir(dir);
    } else {
        perror("Error opening directory");
    }
}

// 设置文件权限
void apply_file_permissions(const char *file_path) {
    if (strstr(file_path, ".sh") || strstr(file_path, ".exe")) {
        chmod(file_path, S_IRWXU);  // 可执行文件，所有者可读写执行
    } else if (strstr(file_path, ".txt") || strstr(file_path, ".md")) {
        chmod(file_path, S_IRUSR | S_IWUSR);  // 文档文件，所有者可读写
    } else {
        chmod(file_path, S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH);  // 其他文件，所有者可读写，其他人只读
    }
}

// 模拟安全检查函数
int perform_security_check(const char *file_path) {
    log_message(file_path);
    return 1; // 模拟通过安全检查
}

// 检查并释放文件
void check_and_release_files(const char *quarantine_dir, const char *source_dir, char ***file_list, int *file_count) {
    DIR *dir;
    struct dirent *ent;

    if ((dir = opendir(quarantine_dir)) != NULL) {
        while ((ent = readdir(dir)) != NULL) {
            if (ent->d_type == DT_REG) {
                char quarantine_path[512], source_path[512];
                snprintf(quarantine_path, sizeof(quarantine_path), "%s/%s", quarantine_dir, ent->d_name);
                snprintf(source_path, sizeof(source_path), "%s/%s", source_dir, ent->d_name);
                
                if (perform_security_check(quarantine_path)) {
                    if (move_file(quarantine_path, source_path) == 0) {
                        char log_msg[512];
                        snprintf(log_msg, sizeof(log_msg), "Released: %s to %s", quarantine_path, source_path);
                        log_message(log_msg);

                        // 更新文件列表
                        (*file_count)++;
                        *file_list = realloc(*file_list, sizeof(char *) * (*file_count));
                        (*file_list)[(*file_count) - 1] = strdup(ent->d_name);
                    }
                }
            }
        }
        closedir(dir);
    } else {
        perror("Error opening directory");
    }
}

int main() {
    const char *source_directory = "safe_files";
    const char *quarantine_directory = "quarantine";
    const char *file_list_path = "file_list.txt";

    char **file_list;
    int file_count;

    if (load_file_list(file_list_path, &file_list, &file_count) != 0) {
        perror("Error loading file list");
        return EXIT_FAILURE;
    }

    isolate_files(source_directory, quarantine_directory, file_list, file_count);

    // 禁用隔离区文件的执行权限
    DIR *dir;
    struct dirent *ent;
    if ((dir = opendir(quarantine_directory)) != NULL) {
        while ((ent = readdir(dir)) != NULL) {
            if (ent->d_type == DT_REG) {
                char file_path[512];
                snprintf(file_path, sizeof(file_path), "%s/%s", quarantine_directory, ent->d_name);
                chmod(file_path, S_IRUSR | S_IWUSR);  // 禁用执行权限
                // 需要特定的网络禁用实现，例如iptables等，这里省略
            }
        }
        closedir(dir);
    }

    check_and_release_files(quarantine_directory, source_directory, &file_list, &file_count);

    if (save_file_list(file_list_path, file_list, file_count) != 0) {
        perror("Error saving file list");
        return EXIT_FAILURE;
    }

    for (int i = 0; i < file_count; i++) {
        free(file_list[i]);
    }
    free(file_list);

    return EXIT_SUCCESS;
}

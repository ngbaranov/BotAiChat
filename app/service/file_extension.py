TEXT_EXTS = {
    ".txt", ".md",
    ".py", ".log", ".out", ".err",
    ".json", ".yaml", ".yml", ".ini", ".cfg", ".conf", ".toml", ".env", ".gitignore", ".dockerignore",
    ".xml", ".html", ".htm", ".css", ".js", ".ts", ".tsx", ".vue",
    ".c", ".cpp", ".h", ".hpp", ".java", ".kt", ".rs", ".go", ".rb", ".php", ".pl", ".swift", ".r", ".sql",
    ".properties", ".gradle", ".make", ".mk", ".bat", ".ps1", ".sh", ".bash", ".zsh",
    ".csv",  # читаем как обычный текст без pandas
}

CANDIDATE_ENCODINGS = ("utf-8", "utf-16", "cp1251", "latin-1")
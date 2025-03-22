DOCKER_PATH := $(shell which docker)
PROJECT_PATH := $(PWD)
LOG_FILE := $(PROJECT_PATH)/cron.log
ENV_FILE := $(PROJECT_PATH)/.env
SUBTITLES_DIR := $(PROJECT_PATH)/subtitles
DOWNLOADED_JSON := $(PROJECT_PATH)/downloaded.json
IMAGE_NAME := youtube-sub-crawler

# 建置 Docker Image
build:
	$(DOCKER_PATH) build -t $(IMAGE_NAME) .

# 手動執行一次
run:
	$(DOCKER_PATH) run --rm --env-file $(ENV_FILE) \
		-v $(SUBTITLES_DIR):/app/subtitles \
		-v $(DOWNLOADED_JSON):/app/downloaded.json \
		$(IMAGE_NAME)

# 加入排程（每天 22:00）
cron:
	(crontab -l 2>/dev/null | grep -v 'youtube-sub-crawler'; \
	 echo "00 22 * * * echo '========== $$(date) Start ==========' >> $(LOG_FILE) && $(DOCKER_PATH) run --rm --env-file $(ENV_FILE) -v $(SUBTITLES_DIR):/app/subtitles -v $(DOWNLOADED_JSON):/app/downloaded.json $(IMAGE_NAME) >> $(LOG_FILE) 2>&1") | crontab -
	@echo "✅ 已成功加入 cron 排程 (每天 22:00 執行)"

# 查看目前 cron 排程
show-cron:
	crontab -l

# 移除排程
remove-cron:
	(crontab -l 2>/dev/null | grep -v 'youtube-sub-crawler') | crontab -
	@echo "✅ 已移除 cron 排程"

# 清空 log
log-clean:
	truncate -s 0 $(LOG_FILE)
	@echo "✅ cron.log 已清空"

# 清理無用 Docker image
prune:
	$(DOCKER_PATH) system prune -f

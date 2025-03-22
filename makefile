IMAGE_NAME = youtube-sub-crawler
VOLUME_PATH = $(shell pwd)/subtitles
CRON_SCHEDULE = 0 22 * * *   # 每天晚上10點執行
CRON_CMD = docker run --rm --env-file $(shell pwd)/.env -v $(VOLUME_PATH):/app/subtitles $(IMAGE_NAME)

.PHONY: build run clean logs prune images cron show-cron

# 建 image
build:
	docker build -t $(IMAGE_NAME) .

# 執行一次
run:
	docker run --rm --env-file .env \
	-v $(PWD)/subtitles:/app/subtitles \
	-v $(PWD)/downloaded.json:/app/downloaded.json \
	youtube-sub-crawler
	
# 刪 image
clean:
	docker rmi $(IMAGE_NAME) || true

# 清光無用資源
prune:
	docker system prune -a -f

# 看 images
images:
	docker images

# 自動寫入 crontab
cron:
	(crontab -l 2>/dev/null | grep -v '$(IMAGE_NAME)'; echo "$(CRON_SCHEDULE) $(CRON_CMD) >> $(shell pwd)/cron.log 2>&1") | crontab -
	@echo "✅ 已成功加入 cron 排程"

# 查看目前 crontab
show-cron:
	crontab -l | grep $(IMAGE_NAME) || echo "⚠️ 尚未排程"

# 移除這個 cron 排程
remove-cron:
	(crontab -l | grep -v '$(IMAGE_NAME)') | crontab -
	@echo "✅ 已移除排程"

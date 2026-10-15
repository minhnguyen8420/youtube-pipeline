# YouTube Data ETL Pipeline

Pipeline ETL thu thập dữ liệu video và bình luận từ các kênh YouTube qua **YouTube Data API v3**, chuẩn hoá bằng **pandas** và nạp vào **Google BigQuery**.

## Luồng xử lý

```
channels.json
     │
     ▼
[Extract]  YouTube Data API v3
  ├─ playlists().list        → danh sách playlist của mỗi kênh
  ├─ playlistItems().list    → video ID trong mỗi playlist
  ├─ videos().list           → thông tin + thống kê video (tối đa 50 ID/lần gọi)
  └─ commentThreads().list   → bình luận cấp cao nhất của từng video
     │
     ▼
[Transform] ép kiểu cột (string / Int64), thêm channel_name, playlist_name, extraction_date
     │
     ▼
[Load]     BigQuery (WRITE_APPEND)
  ├─ YOUTUBE_DATA.video_details
  └─ YOUTUBE_DATA.video_comments
```

Mọi lời gọi API đều tự động phân trang (`list_next`) để lấy đủ dữ liệu.

## Cấu trúc thư mục

```
big_project_1/
├── main.py              # Điểm chạy chính, điều phối toàn bộ ETL
├── run_pipeline.sh      # Script chạy pipeline (dùng cho cron)
├── channels.json        # Danh sách kênh YouTube cần thu thập
├── requirements.txt
├── etl/
│   ├── extract.py       # Gọi YouTube Data API
│   ├── transform.py     # Ép kiểu cột DataFrame
│   └── load.py          # Nạp DataFrame vào BigQuery
├── utils/
│   ├── io.py            # Đọc/ghi JSON, xuất CSV
│   └── logger.py        # Cấu hình logging
└── data/                # Dữ liệu mẫu & notebook thử kết nối (không commit)
```

## Yêu cầu

- Python 3.10+
- YouTube Data API key ([Google Cloud Console](https://console.cloud.google.com/apis/library/youtube.googleapis.com))
- Một Google Cloud project có bật BigQuery, cùng service account có quyền **BigQuery Data Editor** và **BigQuery Job User**

## Cài đặt

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Cấu hình

1. **API key** — tạo file `.env` ở thư mục gốc:

   ```env
   YOUTUBE_API_KEY=your_youtube_api_key
   ```

2. **BigQuery credentials** — đặt file key của service account (ví dụ `bigquery_key.json`) vào thư mục gốc và trỏ biến môi trường tới nó:

   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/bigquery_key.json"
   ```

3. **Danh sách kênh** — chỉnh `channels.json`:

   ```json
   [
       { "channel_name": "SOOBIN Official", "channel_id": "UCpVvunMbMvVj9DgCiOSBdcg" },
       { "channel_name": "The Flob", "channel_id": "UC_2y85xY58cz64hpxJHYlxg" }
   ]
   ```

4. **Bảng đích** — tên bảng BigQuery đang được khai báo trực tiếp trong `main.py` (`video_table`, `comment_table`). Sửa lại nếu dùng project/dataset khác.

> `.env`, `*key.json`, `data/`, `*.csv` và `logs/` đã nằm trong `.gitignore` — không commit secrets.

## Chạy pipeline

Chạy thủ công:

```bash
python main.py
```

Chạy theo lịch bằng cron (log ghi vào `logs/cron.log`, cần tạo thư mục trước):

```bash
mkdir -p logs
chmod +x run_pipeline.sh
crontab -e
# Chạy lúc 07:00 và 23:00 mỗi ngày (giờ máy, UTC+7)
0 7,23 * * * /bin/bash "/Users/minhnn/Data/Data Engineer/big_project_1/run_pipeline.sh"
```

Cron chạy theo múi giờ của máy. Nếu máy không ở UTC+7, thêm `CRON_TZ=Asia/Ho_Chi_Minh` lên đầu crontab (cron trên macOS bỏ qua biến này, nên khi đó phải tự quy đổi giờ).

`run_pipeline.sh` dùng đường dẫn tuyệt đối — sửa lại nếu clone project sang máy khác.

## Schema dữ liệu

### `video_details`

| Cột | Kiểu | Mô tả |
|---|---|---|
| `video_id` | STRING | ID video |
| `title` | STRING | Tiêu đề |
| `published_at` | STRING | Thời điểm đăng (ISO 8601, UTC) |
| `view_count` | INTEGER | Lượt xem |
| `like_count` | INTEGER | Lượt thích |
| `comment_count` | INTEGER | Số bình luận |
| `channel_name` | STRING | Tên kênh (từ `channels.json`) |
| `playlist_name` | STRING | Tên playlist chứa video |
| `extraction_date` | STRING | Thời điểm trích xuất (`YYYY-MM-DD HH:MM:SS`) |

### `video_comments`

| Cột | Kiểu | Mô tả |
|---|---|---|
| `comment_id` | STRING | ID comment thread |
| `video_id` | STRING | ID video |
| `author` | STRING | Tên hiển thị người bình luận |
| `text_display` | STRING | Nội dung (dạng hiển thị, có thể chứa HTML) |
| `text_original` | STRING | Nội dung gốc |
| `published_at` | STRING | Thời điểm đăng |
| `updated_at` | STRING | Thời điểm sửa gần nhất |
| `like_count` | INTEGER | Lượt thích |
| `extraction_date` | STRING | Thời điểm trích xuất |

## Lưu ý

- **Quota API**: YouTube Data API mặc định 10.000 units/ngày; mỗi lời gọi `list` tốn 1 unit. Lấy toàn bộ bình luận của các video nhiều tương tác có thể tốn đáng kể — có thể giới hạn bằng tham số `max_comments` của `get_video_comments()`.
- **Dữ liệu tích luỹ**: bảng được ghi theo chế độ `WRITE_APPEND`, mỗi lần chạy thêm một snapshot mới. Dùng `extraction_date` để lọc bản ghi mới nhất hoặc theo dõi biến động theo thời gian.
- Video có bình luận bị tắt sẽ trả về lỗi HTTP 403 và được bỏ qua (ghi log lỗi).

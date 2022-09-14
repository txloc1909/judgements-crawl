# README

## Arguments

### `-l`, `--level`: Cấp tòa án
- `TW`: TAND tối cao
- `CW`: TAND cấp cao
- `T`: TAND cấp tỉnh
- `H`: TAND cấp huyện

### `-j`, `--judgement`: Bản án/quyết định
- `0`: Bản án
- `1`: Quyết định

### `-c`, `--court`: Tòa án
Đường dẫn đến file `.txt` chứa tên tòa án

### `-t`, `--type`: Loại vụ/việc
- `50`: Hình sự
- `0`: Dân sự
- `1`: Hôn nhân và gia đình
- `2`: Kinh doanh thương mại
- `4`: Hành chính
- `3`: Lao động
- `5`: Quyết định tuyên bố phá sản
- `11`: Quyết định áp dụng biện pháp xử lý hành chính

### `--keyword_file`: Các từ khóa
Đường dẫn đến file `.txt` chứa các từ khóa, mỗi từ khóa trên một dòng

### `--start_from`: Trang bắt đầu tìm

## Example
```bash
python main.py --level T --judgement 0 --court court.txt --type 0 --keyword_file keywords.txt
```

```bash
python main.py --level T --judgement 0 --court court.txt --type 0 --keyword_file keywords.txt --start_from 10
```

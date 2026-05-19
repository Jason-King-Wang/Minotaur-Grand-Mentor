# Data Folder

本資料夾保留給 Z3B-Prime 的本機資料。

建議結構：

```text
data/
  raw/
  processed/
  cache/
```

大型行情資料、快取、券商或交易相關 runtime 檔案都應維持 local-only，不要放入公開發布範圍。

`sample/` 內保留一組極小 synthetic OHLCV，只用來驗證 CLI 與輸出流程，不代表任何真實標的或績效。

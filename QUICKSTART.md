# 🚀 빠른 시작 가이드

## 1️⃣ 설정 (첫 실행만)

```powershell
cd C:\temp\ai-daily-report

# 관리자로 PowerShell 실행 후
.\scripts\install-task.ps1
```

매일 06:00 AM에 자동 실행됩니다.

## 2️⃣ 수동 실행

```powershell
.\scripts\run.ps1
```

## 3️⃣ 리포트 보기

```powershell
# 최신 리포트 열기
Start-Process ".\reports\latest.html"
```

## 🔧 API 키 설정 (선택사항)

`.env` 파일 편집:
```
ANTHROPIC_API_KEY=your_key
```

## 📁 파일 위치

- 리포트: `C:\temp\ai-daily-report\reports\latest.html`
- 로그: `C:\temp\ai-daily-report\data\logs\`
- 설정: `C:\temp\ai-daily-report\config\settings.py`

## ✨ 기능

✅ 자동 뉴스 수집 (65개/실행)
✅ HTML 리포트 생성
✅ 카테고리 분류
✅ 매일 06:00 AM 자동 실행

---

**완성!** 🎉 시스템이 작동 중입니다.

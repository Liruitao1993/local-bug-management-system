@echo off
title BUG����ϵͳ
echo.
echo ========================================
echo    BUG����ϵͳ v1.0 - ��Яʽ�汾
echo ========================================
echo.
echo ���ڼ��Python����...

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ����: δ�ҵ�Python����
    echo.
    echo ���Ȱ�װPython 3.7����߰汾
    echo ���ص�ַ: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Python�������ͨ��
echo.
echo ���ڰ�װ������...
python -m pip install -r requirements.txt --quiet --user

if %errorlevel% neq 0 (
    echo.
    echo ����: ĳЩ��������װʧ�ܣ����Կɳ�������
    echo.
)

echo.
echo ��������BUG����ϵͳ...
echo ϵͳ����������д�: http://localhost:8501
echo �� Ctrl+C �����˳�����
echo.
echo ========================================
echo.

python -m streamlit run app.py --server.headless=true --server.port=8501

if %errorlevel% neq 0 (
    echo.
    echo ����ʧ�ܣ����������Ϣ
    echo.
    pause
)

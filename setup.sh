mkdir -p ~/.streamlit/
echo "
[general]n
email = "anilkumar1988@gmail.com"n
" > ~/.streamlit/credentials.toml
echo "
[server]n
headless = truen
enableCORS=falsen
port = 8501n
" > ~/.streamlit/config.toml
mkdir -p ~/.streamlit/
echo "[general]\nemail=anilkumar1988@gmail.com\n" > ~/.streamlit/credentials.toml
echo "[server]\nheadless=true\nenableCORS=false\nport = $PORT\n" > ~/.streamlit/config.toml
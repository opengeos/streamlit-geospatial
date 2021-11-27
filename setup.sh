# sudo add-apt-repository ppa:ubuntugis/ppa && sudo apt-get update
# sudo apt-get update
# sudo apt-get install python3-dev
# sudo apt-get install gdal-bin
# sudo apt-get install libgdal-dev
# export CPLUS_INCLUDE_PATH=/usr/include/gdal
# export C_INCLUDE_PATH=/usr/include/gdal
# gdal-config --version
# pip install GDAL==$(gdal-config --version | awk -F'[.]' '{print $1"."$2}') localtileserver

mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
From bash:latest

# COPY ca.crt /ca.crt
ENV http_proxy "http://proxy-dmz.intel.com:911"
ENV https_proxy "http://proxy-dmz.intel.com:912"

# These two lines are required in order to incorporate runtime args with the image entrypoint and cmd
COPY entry_script_bash.sh /usr/local/bin/entry_script_bash.sh
ENTRYPOINT ["/bin/bash", "/usr/local/bin/entry_script_bash.sh"]

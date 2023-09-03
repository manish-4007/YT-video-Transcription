
mkdir -p ~/.config/ImageMagick
chmod +w ~/.config/ImageMagick
# chmod +r /etc/ImageMagick-6/policy.xml
# chmod +w /home/appuser/.config/ImageMagick/policy.xml


# ./magick -list policy

# cat ~/.config/ImageMagick/policy.xml
# <policymap>
#     <policy domain="coder" rights="read|write" pattern="HTTP" />
# </policymap>

# rpm -Uvh ImageMagick-7.1.1-15.x86_64.rpm
# rpm -Uvh ImageMagick-libs-7.1.1-15.x86_64.rpm
# cd $HOME
# tar xvzf ImageMagick.tar.gz
# echo "Fetching Done"
# export MAGICK_HOME="$HOME/ImageMagick-7.1.1"
# export PATH="$MAGICK_HOME/bin:$PATH
# LD_LIBRARY_PATH="${LD_LIBRARY_PATH:+$LD_LIBRARY_PATH:}$MAGICK_HOME/lib
# export LD_LIBRARY_PATH
# magick logo: logo.gif
# identify logo.gif
# display logo.gif
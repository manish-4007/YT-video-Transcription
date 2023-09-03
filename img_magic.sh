#!/bin/bash
# sudo -S chown appuser /etc/ImageMagick-6/policy.xml
# sudo -S chmod u+w /etc/ImageMagick-6/policy.xml
# echo "Fetching Done"
# whoami
# sudo -S cat /etc/ImageMagick-6/policy.xml | sed 's/none/read,write/g' > /etc/ImageMagick-6/policy.xml
#!/bin/sh

# # Specify the paths to the input and output policy.xml files
# input_file="/etc/ImageMagick-6/policy.xml"
# temp_file="/etc/ImageMagick-6/policy_temp.xml"
# output_file="/etc/ImageMagick-6/policy.xml"

# # Use sudo to run sed with elevated permissions
# sudo sed 's/none/read,write/g' "$input_file" > "$temp_file"

# # Use sudo to overwrite the original policy.xml file with the modified contents from the temporary file
# sudo mv "$temp_file" "$output_file"

# # Clean up the temporary file
# rm "$temp_file"

# # Optionally, display a message indicating the operation was successful
# echo "Policy.xml file updated successfully!"

cat /etc/ImageMagick-6/policy.xml | sed 's/none/read,write/g' > custom_policy.xml
cat custom_policy.xml > ~/.config/ImageMagick/policy.xml

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
#!/bin/bash
sudo chmod +w /etc/ImageMagick-6/policy.xml
sudo chmod -R 777 /usr/
sudo chmod -R 777 /root/
echo "Fetching Done"
sudo -S cat /etc/ImageMagick-6/policy.xml | sed 's/none/read,write/g' > /etc/ImageMagick-6/policy.xml
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


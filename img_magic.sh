#!/bin/bash
sudo chmod +w /etc/ImageMagick-6/policy.xml
echo "Fetching Done"
cat /etc/ImageMagick-6/policy.xml | sed 's/none/read,write/g' > /etc/ImageMagick-6/policy.xml

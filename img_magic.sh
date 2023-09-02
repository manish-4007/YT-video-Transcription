#!/bin/bash
sudo chmod +w /etc/ImageMagick-6/policy.xml
cat /etc/ImageMagick-6/policy.xml | sed 's/none/read,write/g' > /etc/ImageMagick-6/policy.xml

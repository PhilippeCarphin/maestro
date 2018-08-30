# Run this script before running 'make' to configure the build process.
# It creates the config.mk file according to user input.

echo "Build version (example: 1.5.1):"
read VERSION

CONFIG_FILENAME="config.mk"
rm -f $CONFIG_FILENAME
echo "
VERSION=$VERSION
" >> $CONFIG_FILENAME

# This script searches for all ssm files in child directories and creates a soft link in the ssm folder.

mkdir -p ssm
for path in `find . -name *.ssm -exec readlink -f {} \;` ; do
		filename=`basename $path`
		rm -f ssm/$filename
		ln -s $path ssm/$filename
done

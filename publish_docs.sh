docbuild='doc/_build'

cd doc
echo '# Making docs'
make all
cd ../

echo '# Building tarball of docs'
mkdir _tmpdoc
cp -pr doc/*.pdf     _tmpdoc/.
cp -pr doc/_build/html/*   _tmpdoc/.
cd _tmpdoc
tar czf ../../_docs.tgz .
cd ..
rm -rf _tmpdoc

#

echo "# Switching to gh-pages branch"
git checkout gh-pages

if  [ $? -ne 0 ]  ; then
  echo ' failed.'
  exit
fi

tar xzf ../_docs.tgz .

echo "# commit changes to gh-pages branch"
git add *.html
git commit -am "updated docs"

if  [ $? -ne 0 ]  ; then
  echo ' failed.'
  exit
fi

echo "# Pushing docs to github"
git push


echo "# switch back to master branch"
git checkout master

if  [ $? -ne 0 ]  ; then
  echo ' failed.'
  exit
fi


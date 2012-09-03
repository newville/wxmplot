docbuild='doc/_build'

cd doc
echo '# Making docs'
rm -rf _build/
make all

echo '# Building tarball of docs'
cd _build/html
tar czf ../../_docs.tgz .
cd ../..
#

echo "# Switching to gh-pages branch"
git checkout gh-pages

if  [ $? -ne 0 ]  ; then
  echo ' failed.'
  exit
fi

tar xzf _docs.tgz .

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


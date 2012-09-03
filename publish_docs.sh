
# assumes full doc is already created -- we're installing
# doc/_build/html as gh-pages

cd doc/_build/html
tar czf ../../../_docs.tgz .
cd ../../../

echo "# Switching to gh-pages branch"
git checkout gh-pages

if  [ $? -ne 0 ]  ; then
  echo ' failed.'
  exit
fi

tar xzf _docs.tgz .

echo "# commit changes to gh-pages branch"
git add *.html _images/* _static/*
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


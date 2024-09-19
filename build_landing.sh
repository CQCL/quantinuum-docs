cd landing
npm ci --frozen-lockfile
npm run build
cp -R out/. ../base_site/.
cd ..

rm -rf build
npx tsup 
cp ./node_modules/@cqcl/quantinuum-ui/dist/tokens.css ./build/tokens.css
npx tailwindcss --postcss ./postcss.config.cjs -i ./src/index.css -o ./build/styles.css

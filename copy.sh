rm -rf ./addons/base_ecommerce/
rm -rf ./addons/oeoo_amazon/
rm -rf ./addons/product_images_olbs/
rm -rf ./addons/subscription_saas/

cp -r /home/yinshuwei/python/openerp-v7/openerp/addons/base_ecommerce/ ./addons/base_ecommerce/
cp -r /home/yinshuwei/python/openerp-v7/openerp/addons/oeoo_amazon/ ./addons/oeoo_amazon/
cp -r /home/yinshuwei/python/openerp-v7/openerp/addons/product_images_olbs/ ./addons/product_images_olbs/
cp -r /home/yinshuwei/python/openerp-v7/openerp/addons/subscription_saas/ ./addons/subscription_saas/

find ./ -name "*.pyc" | xargs -i -t rm -f {}
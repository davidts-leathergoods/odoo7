#!/bin/sh
cd `dirname $0`
ROOT_PATH_Header=`pwd`
ROOT_PATH=`pwd`
cd ~
if [ -d sale_files ]
then
	echo "file existe"
else 
	mkdir sale_files

fi
cd sale_files
PATH_FILES=`pwd` 
cd $ROOT_PATH
 java -Xms256M -Xmx2024M -cp $ROOT_PATH/../lib/trove.jar:$ROOT_PATH/../lib/jboss-serialization.jar:$ROOT_PATH/../lib/filecopy.jar:$ROOT_PATH/../lib/jakarta-oro-2.0.8.jar:$ROOT_PATH/../lib/advancedPersistentLookupLib-1.0.jar:$ROOT_PATH/../lib/talend_file_enhanced_20070724.jar:$ROOT_PATH/../lib/ganymed-ssh2.jar:$ROOT_PATH/../lib/talendcsv.jar:$ROOT_PATH/../lib/postgresql-8.3-603.jdbc3.jar:$ROOT_PATH/../lib/dom4j-1.6.1.jar:$ROOT_PATH/../lib/commons-collections-3.2.jar:$ROOT_PATH/../lib/log4j-1.2.15.jar:$ROOT_PATH:$ROOT_PATH/../lib/systemRoutines.jar::$ROOT_PATH/../lib/userRoutines.jar::.:$ROOT_PATH/sale_openerpwms_0_1.jar: talendopenerp.sale_openerpwms_0_1.sale_openerpwms --context_param picking_id=$1 \
--context_param Path_Header_sale=$ROOT_PATH_Header \
--context_param Path_files=$PATH_FILES \

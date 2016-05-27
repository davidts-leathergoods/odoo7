#!/bin/sh
cd `dirname $0`
ROOT_PATH_Header=`pwd`
ROOT_PATH=`pwd`
cd ~
if [ -d purchase_files ]
then
	echo "file existe"
else 
	mkdir purchase_files

fi
cd purchase_files
PATH_FILES=`pwd` 
cd $ROOT_PATH
 java -Xms256M -Xmx2024M -cp $ROOT_PATH/../lib/trove.jar:$ROOT_PATH/../lib/jboss-serialization.jar:$ROOT_PATH/../lib/filecopy.jar:$ROOT_PATH/../lib/jakarta-oro-2.0.8.jar:$ROOT_PATH/../lib/advancedPersistentLookupLib-1.0.jar:$ROOT_PATH/../lib/talend_file_enhanced_20070724.jar:$ROOT_PATH/../lib/ganymed-ssh2.jar:$ROOT_PATH/../lib/talendcsv.jar:$ROOT_PATH/../lib/postgresql-8.3-603.jdbc3.jar:$ROOT_PATH/../lib/dom4j-1.6.1.jar:$ROOT_PATH/../lib/commons-collections-3.2.jar:$ROOT_PATH/../lib/log4j-1.2.15.jar:$ROOT_PATH:$ROOT_PATH/../lib/systemRoutines.jar::$ROOT_PATH/../lib/userRoutines.jar::.:$ROOT_PATH/purchase_openerpwms_0_1.jar: talendopenerp.purchase_openerpwms_0_1.purchase_openerpwms --context_param picking_id=$1 \
--context_param Path_Header=$ROOT_PATH_Header \
--context_param Path_files=$PATH_FILES \

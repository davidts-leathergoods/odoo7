#!/bin/sh
cd `dirname $0`
ROOT_PATH_Header=`pwd`
 ROOT_PATH=`pwd`
cd ~
if [ -d archive_files ]
then
	echo "file existe"
else
	mkdir archive_files

fi
cd archive_files
ARCHIVE_FILES=`pwd`
cd $ROOT_PATH
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
 java -Xms256M -Xmx2024M -cp $ROOT_PATH/../lib/trove.jar:$ROOT_PATH/../lib/jboss-serialization.jar:$ROOT_PATH/../lib/filecopy.jar:$ROOT_PATH/../lib/jakarta-oro-2.0.8.jar:$ROOT_PATH/../lib/advancedPersistentLookupLib-1.0.jar:$ROOT_PATH/../lib/talend_file_enhanced_20070724.jar:$ROOT_PATH/../lib/ganymed-ssh2.jar:$ROOT_PATH/../lib/talendcsv.jar:$ROOT_PATH/../lib/postgresql-8.3-603.jdbc3.jar:$ROOT_PATH/../lib/dom4j-1.6.1.jar:$ROOT_PATH/../lib/commons-collections-3.2.jar:$ROOT_PATH/../lib/log4j-1.2.15.jar:$ROOT_PATH:$ROOT_PATH/../lib/systemRoutines.jar::$ROOT_PATH/../lib/userRoutines.jar::.:$ROOT_PATH/wms_openerp_purchase_0_1.jar: talendopenerp_213.wms_openerp_purchase_0_1.wms_openerp_purchase --context_param Path_wms_files_purchase=$PATH_FILES \
--context_param path_wms_archive=$ARCHIVE_FILES \

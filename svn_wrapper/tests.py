from django.test import TestCase
import pysvn
import os

# Create your tests here.

def get_log_message():
    return True, 'test'

def notify( event_dict ):
    #print event_dict
    if str(event_dict['action']) == 'tree_conflict':
        print event_dict['path']
    return

def conflict_resolver( conflict_description ):
    #print conflict_description
    return conflict_choice, merge_file, save_merged


client = pysvn.Client()
client.callback_get_log_message = get_log_message

#client.mkdir('svn://192.168.1.204/trunk/8899/', '')
#client.checkin()



#print client.update('/usr/local/svn/')
#ls = client.list('svn://192.168.1.204/trunk/12333')
#print ls
#for (f,i) in ls:
#   print f.kind

#client.copy('svn://192.168.1.204/trunk/maven/', 'svn://192.168.1.204/branches/bbb/0987')

#print client.checkin('/usr/local/svn/trunk/11226/','')

#print client.mkdir('svn://192.168.1.204/trunk/1234/', '')

#x = os.listdir('/usr/local/svn/trunk/')
#print x

#FROM_URL = r'svn://192.168.1.204/branches/maven/haha/'
WC_PATH = '/usr/local/svn/trunk/maven/'
WC_PATH2 = '/usr/local/svn/branches/maven/haha/'

#r = 54
#print client.merge_peg(FROM_URL, pysvn.Revision(pysvn.opt_revision_kind.number, r-1),pysvn.Revision(pysvn.opt_revision_kind.number, r),pysvn.Revision(pysvn.opt_revision_kind.head),WC_PATH)


#FROM_URL = r'/usr/local/svn/branches/maven/haha/'
FROM_URL = 'svn://192.168.1.204/branches/maven/haha/'
TO_URL = 'svn://192.168.1.204/trunk/maven/'

client.update('/usr/local/svn/')
client.callback_notify = notify
client.callback_conflict_resolver = conflict_resolver

print client.merge_reintegrate(WC_PATH2, pysvn.Revision(pysvn.opt_revision_kind.head), WC_PATH, dry_run=True)

#client.merge(FROM_URL, pysvn.Revision(pysvn.opt_revision_kind.head), TO_URL, pysvn.Revision(pysvn.opt_revision_kind.head), WC_PATH)


#print client.checkin(WC_PATH, '')


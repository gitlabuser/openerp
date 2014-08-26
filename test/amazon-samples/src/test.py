# -*- coding: UTF-8 -*-

from lxml import objectify

def testUpdate():
    a = {'a':'1', 'b':'2'}
    b = {'a':'3', 'c':'4'}
    
    print a
    print b
    
    b.update(a)
    print b

def testXml():
    xml = '''<main>
<object1 attr="name">content</object1>
<object1 attr="foo">contenbar</object1>
<test>me</test>
</main>
    '''
    
    print "start...."
    obj = objectify.fromstring(xml).to
    print obj.object1[0]
    print obj.test
    
testXml()

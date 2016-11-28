## 说明
----
* 代码：
    * 新增：
    	* /usr/local/OneOps-master/jenkins_wrapper
    	* /usr/local/OneOps-master/templates/jenkins_wrapper
    * 修改：
	* /usr/local/OneOps-master/saltshaker/settings.py
	* /usr/local/OneOps-master/saltshaker/urls.py
	* /usr/local/OneOps-master/templates/base.html

		
2. 环境：
	* jenkins:
		* 新环境部署，需要部署205上的/usr/lib/python2.7/site-packages/jenkins/
	* six:
		* 更新six库版本，本地库版本太旧（pip uninstall six; pip install six)

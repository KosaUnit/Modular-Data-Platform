mc alias set mini-bronze http://localhost:9000 Admin Pass1234
mc mb mini-bronze/my-bucket
mc admin user add mini-bronze bronzeUser1 Pass1234
mc admin user svcacct add mini-bronze bronzeUser1
mc admin policy attach mini-bronze readwrite --user bronzeUser1
mc admin user svcacct add mini-bronze bronzeUser1
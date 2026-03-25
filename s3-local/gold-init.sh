mc alias set mini-gold http://localhost:9000 Admin Pass1234
mc mb mini-gold/my-gold-bucket
mc admin user add mini-gold goldUser1 Pass1234
mc admin user svcacct add mini-gold goldUser1
mc admin policy attach mini-gold readwrite --user goldUser1
mc admin user svcacct add mini-gold goldUser1
https://www.jianshu.com/p/88b7be4657a3
https://segmentfault.com/a/1190000008481722
https://www.kancloud.cn/kancloud/rest-api-design-safety/78111
https://www.cnblogs.com/vovlie/p/4182814.html

- Basic Auth
- Cookie/Session Auth

综合为flask_login

- Oauth1.0a或者Oauth2

 侧重于一个应用介入另一个应用，微信登录,谷歌登录等

- Token Auth(API KEY)

 md5加key，itsdangerous，有效时间
 重置密码链接
 

- JWT

待研究



# Basic Auth

这种认证直接顺应HTTP协议的无状态性，每次执行业务的时候，都暴力地附带username与password参数，
并将其发送给服务器进行验证。尽管在服务器端可以优雅地使用AOP技术（如拦截器或动态代理）对所有controller进行前置的登录验证。
但如果每次验证都要查数据库的话，创建连接与查询操作势必会增大开销。如果服务器端不做任何记忆（有状态性）处理的话，那么这种方式就已经没有其他办法可以优化了。

#Cookie/Session Auth

上面已经点到，只要服务器端稍加一些记忆处理（记录哪些用户登录过）即可大大优化这个过程：只需要在用户第一次登录系统的时候，
将对应的username放入一个类似与Set<String>的数据结构中。只要登录一次（保证不退出），那么当用户第二次访问controller的时候，
只需要查询Set<String>中是否有该username即可。但这种方式仍有不足，即每次还是必须要求客户端传username过来，否则服务器端不知道是谁就无法判断了。
要优雅地解决上述问题，就要得益于后来HTTP协议中出现的Cookie与Session技术了。当浏览器利用HTTP协议访问服务器的时候，服务器会为其自动创建一个其独有的session对象。
session在基本的数据结构上类似于键值对Map，但不同的是它还提供了若干操作方法，且可以设置时效。既然一个浏览器唯一对应了一个session，那就好办了，
用户第一次登录验证成功后，就可把用户名写入session中表征当前处于该浏览器上的用户已经登录，以后访问controller只用查session中是否有username键即可，若有放行，若没有则阻止.：


为了不每次都传输账号密码 
使用cookie自动携带session_id(session_id保存在cookie里)
，session通过cookie的session_id自动认证出current_user, 
为了安全加信息加密，服务端设置secret_ky,并且使用SSL 


API KEY

https://www.kancloud.cn/kancloud/rest-api-design-safety/78111


Oauth1.0a或者Oauth2


JWT

Token Auth

第一次登录
用户携带username与password请求第一次登录（为保证安全性通常采用HTTPS协议传输）；
服务器接收到后，查询数据库看用户是否存在且密码（MD5加密后）是否匹配，若匹配，则在用户表中查询该用户信息（角色、权限、状态等）；
从配置文件中读取签名的私钥，并整合上一步得到的用户信息生成token（可采用第三方库JWT lib）；
将token写入cookie并重定向到前端。

登录后访问业务
用户携带从cookie（若为移动终端，可以是数据库或文件系统）取出的token访问需登录及特定权限的业务；
请求首先被认证拦截器拦截，并获取到传来的token值；
根据配置文件中的签名私钥，结合JWT lib进行解密与解码；
验证签名是否正确（若不正确JWT会抛出异常）、token是否过期与接收方是否是自己（由自己判断）等。若通过则证明用户已登录，进入权限验证阶段；
通过权限验证框架（shiro、spring security等）验证用户是否具有访问该业务的权限，若有则返回相应数据。

认证方式比较
1.cookie支持问题
session和cookie其实是紧密相联的。浏览器与服务器首次建立连接的时候，服务器会自动生成一个会话号sid，并写入响应报文的首部字段<Set-cookie>中，返回给客户端让其存入cookie。之后每次的HTTP请求报文中均会在首部写入cookie中的sid，服务器接收到后根据sid取出对应session，再进一步根据username键是否存在判断登录与否。
可以看出cookie/session认证要求客户端必须支持cookie技术，但很显然，客户端并不是只能为浏览器，还可以是PC桌面、移动终端等其它平台，对于这些平台，我们无法保证他们都能支持cookie技术。而token认证只认token这个字符串值，至于前端是浏览器采用cookie存的token还是Android终端用数据库存的token都无所谓，只要拿到token值即可进行验证。

2.session共享问题
session是无法在多台服务器之间共享的，特别在分布式部署环境（即多台部署了同一系统的Web服务器集群）下将带来很多同步、一致性问题。比如下面这个场景：
用户请求登录，HTTP请求被转发到了服务器A，在A上完成认证后将登录状态记录到了session；
用户后续请求其他需登录的业务，HTTP请求被转发到了非A的服务器上，这时由于这些服务器上的session并非A上的session，所以其上就没有登录状态记录，所以业务操作将被拒绝！
很显然这时采用cookie/session认证就很棘手了，需要自己去维护同步、状态一致等问题。而token根本不会依赖session，所有服务器都是一致地采用私钥+解密算法分析签名的正确性。

3 时间/空间开销问题
如果session不仅是要存储用户名，还要存储时效时间、登录时间等各种状态信息（特别是大型系统），那么一旦登录的用户数激增，服务器的内存消耗也将急剧增大。而token认证是完全将状态存入了token值中，再利用加解密算法将状态取出，用时间复杂度换取了空间复杂度，内存开销大大减小，时间效率有降低。

4 第三方授权问题
采用传统认证方式，若要访问业务，一定要先登录。假如这时一个第三方应用希望获取该用户在本系统的一些资源（如头像、昵称、签名等），则一定要先接受登录拦截器认证才可放行，这时如果第三方应用也通过用户名+密码登录的形式来获取信息的话，势必会暴露用户在本系统的信息，很不安全！
而一种更巧妙的做法是，先记录第三方应用的AppID与其url地址，然后跳转到本系统登录页面进行登录，认证成功后，经本系统的认证服务器生成access_token，携带该参数并重定向到url地址所在页面。此后第三方应用即可凭借该access_token的权限范围，访问所需的本系统的资源。
可以看出，无论是本系统自己凭借token访问自己的资源，还是第三方应用凭借access_token访问本系统资源，依靠的都是token这个凭据，走的都是统一的一套流程，而传统方式，需要额外写一套，可维护性很不好。关于第三方认证文章可以参考理解Ouath2.0。

结语
虽然token认证优势非常明显，但仍然需要考虑如下问题：如何抵御跨站脚本攻击（XSS）、如何防范重放攻击（Replay Attacks）、如何防范MITM （Man-In-The-Middle）攻击等。对此本文就不再做详细叙述了。
本文是结合自己理解并参考了如下几篇博文而写（其中还包含JWT lib的使用示例）：

作者：阿堃堃堃堃
链接：https://www.jianshu.com/p/88b7be4657a3
來源：简书
简书著作权归作者所有，任何形式的转载都请联系作者获得授权并注明出处。

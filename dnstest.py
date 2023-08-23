import dns.resolver

# 设置要查询的域名和目标DNS服务器
domain = 'www.zifeng.me'
dns_server = '2606:4700:4700::1111'
#dns_server = '2400:3200::1'

# 使用dnspython解析域名
resolver = dns.resolver.Resolver(configure=False)
resolver.nameservers = [dns_server]
ipv6_address = resolver.resolve(domain, 'AAAA')[0].address

print(ipv6_address)

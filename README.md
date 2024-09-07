# Sslv3Trap
Proxy server for SSLv3, for ancient software.

Accepts traffic from SSLv3 and redirects to the target server, without encryption. It is better to use the server on a single machine, the network where the target server is.

Implemented specifically for ancient software, games and other fossils.

### Specifications
it is written in Python v3.5.0. 3.5 the latest version that has support for this old and insecure protocol.

### How to use
When the server starts, it expects that all the required arguments have been passed to it. More precisely, he needs to specify the paths to the certificate and private key:

` --path_cert=./cert.pem --path_key=./priv_key.pem `

The server startup usually depends on the OS where it will happen. Here's how it usually happens in Windows (reminder :)):

` ./SSLv3Trap.exe --path_cert=./cert.pem --path_key=./priv_key.pem `

There are also a few more arguments:
|Code|Description|default|
|-|--------|---|
|`--target_server_address`|Address of the target server|127.0.0.1|
|`--target_server_port`|Port of the target server|19120|
|`--proxy_server_address`|Address of the proxy server|127.0.0.1|
|`--proxy_server_port`|Port of the proxy server|19100|
|`--has_debug`|For the developer, outputs more info to console|false|
|`--path_cert`|Path to the certificate|-|
|`--path_key`|Path to the private key|-|

### Additionally
I don't know who might need it, modern protocols are mostly used now, but as a kind of intermediary between the old client and the new server, maybe.

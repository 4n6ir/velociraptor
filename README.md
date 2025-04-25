# velociraptor

### Server

1. ```wget https://github.com/Velocidex/velociraptor/releases/download/v0.74/velociraptor-v0.74.1-linux-arm64```
2. ```chmod 750 velociraptor-v0.74.1-linux-arm64```
3. ```./velociraptor-v0.74.1-linux-arm64 config generate -i```
4. ```./velociraptor-v0.74.1-linux-arm64 --config server.config.yaml debian server --binary velociraptor-v0.74.1-linux-arm64```
5. ```dpkg -i velociraptor_server_0.74.1_arm64.deb```
6. ```systemctl status velociraptor_server.service```

### Clients

1. ```./velociraptor-v0.74.1-linux-arm64 --config server.config.yaml config client > client.config.yaml```
2. ```./velociraptor-v0.74.1-linux-arm64 --config client.config.yaml debian client```

    or

   ```./velociraptor-v0.74.1-linux-arm64 --config client.config.yaml rpm client```

3. ```dpkg -i velociraptor_client_0.74.1_arm64.deb```

    or

    ```rpm -i velociraptor_client_0.74.1_aarch64.rpm```

4. ```systemctl status velociraptor_client.service```

### Reference

- https://github.com/Velocidex/velociraptor

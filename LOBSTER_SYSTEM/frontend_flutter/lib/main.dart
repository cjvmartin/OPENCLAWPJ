import 'package:flutter/material.dart';

void main() => runApp(LobsterApp());

class LobsterApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar:
            AppBar(title: Text('🦞 龍蝦外送員端'), backgroundColor: Colors.redAccent),
        body: OrderList(),
      ),
    );
  }
}

class OrderList extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Card(
        margin: EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: Icon(Icons.delivery_dining, color: Colors.red),
              title: Text('高科大餐廳 -> 電機大樓'),
              subtitle: Text('待接單 | 預計收益: \$150'),
            ),
            ElevatedButton(
              onPressed: () {/* 點擊後呼叫 FastAPI */},
              child: Text('立即接單'),
              style:
                  ElevatedButton.styleFrom(backgroundColor: Colors.redAccent),
            ),
            SizedBox(height: 10),
          ],
        ),
      ),
    );
  }
}

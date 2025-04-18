import 'package:flutter/material.dart';
import 'package:solana_mvp/solana_mvp.dart';

void main() => runApp(FarmYieldsApp());

class FarmYieldsApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Farm Yields',
      home: YieldScreen(),
    );
  }
}

class YieldScreen extends StatefulWidget {
  @override
  _YieldScreenState createState() => _YieldScreenState();
}

class _YieldScreenState extends State<YieldScreen> {
  final optimizer = LiquidityMiningOptimizer(OrcaClient());

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Yields')),
      body: FutureBuilder(
        future: optimizer.getTopPools(),
        builder: (context, snapshot) {
          if (!snapshot.hasData) return CircularProgressIndicator();
          final pools = snapshot.data as List<PoolInfo>;
          return ListView(
            children: pools.map((p) => ListTile(
              title: Text(p.pair),
              subtitle: Text('APR: \${p.apr}%'),
            )).toList(),
          );
        },
      ),
    );
  }
}

import 'package:flutter/material.dart';

void main() {
  runApp(const ThermalPrinterApp());
}

class ThermalPrinterApp extends StatelessWidget {
  const ThermalPrinterApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Thermal Printer Manager',
      theme: ThemeData(colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple)),
      home: const PrintJobsScreen(),
    );
  }
}

class PrintJobsScreen extends StatelessWidget {
  const PrintJobsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Fila de Impressão'),
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: () {}),
        ],
      ),
      body: Column(
        children: [
          const PrinterStatusBanner(),
          const SectionHeader(title: 'Trabalhos Pendentes'),
          PrintJobList(jobs: PrintJob.mockPending()),
          const SectionHeader(title: 'Histórico do Dia'),
          PrintJobList(jobs: PrintJob.mockHistory()),
          const PrintSummaryFooter(),
        ],
      ),
    );
  }
}

class PrinterStatusBanner extends StatelessWidget {
  const PrinterStatusBanner({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 80,
      color: Colors.green.shade100,
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: const Row(
        children: [
          Icon(Icons.check_circle, color: Colors.green),
          SizedBox(width: 8),
          Text('Impressora EP-T20 conectada via USB'),
        ],
      ),
    );
  }
}

class SectionHeader extends StatelessWidget {
  final String title;
  const SectionHeader({super.key, required this.title});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 48,
      color: Colors.grey.shade200,
      padding: const EdgeInsets.symmetric(horizontal: 16),
      alignment: Alignment.centerLeft,
      child: Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
    );
  }
}

class PrintJobList extends StatelessWidget {
  final List<PrintJob> jobs;
  const PrintJobList({super.key, required this.jobs});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: jobs.map((job) => PrintJobTile(job: job)).toList(),
    );
  }
}

class PrintJobTile extends StatelessWidget {
  final PrintJob job;
  const PrintJobTile({super.key, required this.job});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 72,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        border: Border(bottom: BorderSide(color: Colors.grey.shade300)),
      ),
      child: Row(
        children: [
          Icon(Icons.print, color: job.isPending ? Colors.orange : Colors.grey),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(job.name, style: const TextStyle(fontWeight: FontWeight.w500)),
                Text(job.timestamp, style: const TextStyle(fontSize: 12, color: Colors.grey)),
              ],
            ),
          ),
          Text('${job.pages}p', style: const TextStyle(color: Colors.grey)),
        ],
      ),
    );
  }
}

class PrintSummaryFooter extends StatelessWidget {
  const PrintSummaryFooter({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 120,
      color: Colors.deepPurple.shade50,
      padding: const EdgeInsets.all(16),
      child: const Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text('Resumo do Turno', style: TextStyle(fontWeight: FontWeight.bold)),
          SizedBox(height: 8),
          Text('Total impresso hoje: 47 documentos — 312 páginas'),
        ],
      ),
    );
  }
}

class PrintJob {
  final String name;
  final String timestamp;
  final int pages;
  final bool isPending;

  const PrintJob({
    required this.name,
    required this.timestamp,
    required this.pages,
    required this.isPending,
  });

  static List<PrintJob> mockPending() => const [
    PrintJob(name: 'Nota Fiscal #4521', timestamp: '14:32 — aguardando', pages: 2, isPending: true),
    PrintJob(name: 'Relatório Diário', timestamp: '14:28 — aguardando', pages: 5, isPending: true),
    PrintJob(name: 'Etiquetas Lote #200', timestamp: '14:15 — aguardando', pages: 1, isPending: true),
  ];

  static List<PrintJob> mockHistory() => const [
    PrintJob(name: 'Nota Fiscal #4520', timestamp: '13:55', pages: 2, isPending: false),
    PrintJob(name: 'Recibo Cliente VIP', timestamp: '13:41', pages: 1, isPending: false),
    PrintJob(name: 'Etiquetas Lote #150', timestamp: '13:30', pages: 1, isPending: false),
    PrintJob(name: 'Relatório Turno A', timestamp: '12:00', pages: 8, isPending: false),
    PrintJob(name: 'Nota Fiscal #4519', timestamp: '11:47', pages: 2, isPending: false),
  ];
}
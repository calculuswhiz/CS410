package edu.illinois.cs.index;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.FieldType;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.IndexWriterConfig.OpenMode;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.util.Version;
import org.apache.lucene.analysis.ja.*;

public class Indexer {

	/**
	 * Creates the initial index files on disk
	 * @param indexPath
	 * @return
	 * @throws IOException
	 */
	private static IndexWriter setupIndex(String indexPath) throws IOException {
		Analyzer analyzer = new JapaneseAnalyzer(Version.LUCENE_46, null, JapaneseTokenizer.Mode.SEARCH, JapaneseAnalyzer.getDefaultStopSet(), JapaneseAnalyzer.getDefaultStopTags());
		IndexWriterConfig config = new IndexWriterConfig(Version.LUCENE_46,
				analyzer);
		config.setOpenMode(OpenMode.CREATE);
		config.setRAMBufferSizeMB(2048.0);

		FSDirectory dir;
		IndexWriter writer = null;
		dir = FSDirectory.open(new File(indexPath));
		writer = new IndexWriter(dir, config);

		return writer;
	}

	/**
	 * @param indexPath
	 *            Where to create the index
	 * @param prefix
	 *            The prefix of all the paths in the fileList
	 * @param fileList
	 *            Each line is a path to a document
	 * @throws IOException
	 */
	public static void index(String indexPath, String prefix, String fileList)
			throws IOException {

		System.out.println("Creating Lucene index...");

		FieldType _urlFieldType = new FieldType();
		_urlFieldType.setIndexed(true);
		_urlFieldType.setStored(true);

		FieldType _titleFieldType = new FieldType();
		_titleFieldType.setIndexed(true);
		_titleFieldType.setStored(true);

		FieldType _artistFieldType = new FieldType();
		_artistFieldType.setIndexed(true);
		_artistFieldType.setStored(true);

		FieldType _langFieldType = new FieldType();
		_langFieldType.setIndexed(true);
		_langFieldType.setStored(true);

		FieldType _contentFieldType = new FieldType();
		_contentFieldType.setIndexed(true);
		_contentFieldType.setStored(true);

		IndexWriter writer = setupIndex(indexPath);
		BufferedReader br = new BufferedReader(
				new FileReader(prefix + fileList));
		String line = null;
		int indexed = 0;
		while ((line = br.readLine()) != null) {

			ArrayList<String> lines = new ArrayList<String>();
			BufferedReader docReader = new BufferedReader(new FileReader(prefix + line));
			String docLine;
			while ((docLine = docReader.readLine()) != null) {
			   lines.add(docLine);
			}
			docReader.close();

			// 1st line: url, 2nd: song title, 3rd: artist/performer,
			// 4th: language, rest: text content
			if (lines.size() < 5)
				continue;
			
			String content = new String();
			for(int i = 4; i < lines.size(); ++i)
				content += lines.get(i) + " ";

			Document doc = new Document();
			doc.add(new Field("url", lines.get(0), _urlFieldType));
			doc.add(new Field("title", lines.get(1), _titleFieldType));
			doc.add(new Field("artist", lines.get(2), _artistFieldType));
			doc.add(new Field("lang", lines.get(3), _langFieldType));
			doc.add(new Field("content", content, _contentFieldType));
			writer.addDocument(doc);

			++indexed;
			if (indexed % 100 == 0)
				System.out.println(" -> indexed " + indexed + " docs...");
		}
		System.out.println(" -> indexed " + indexed + " total docs.");

		br.close();
		writer.close();
	}
}

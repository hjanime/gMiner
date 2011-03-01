import java.io.BufferedReader;
import java.io.IOException;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;

public class Client {    
	// Build parameter string for gMiner
	public static final String content = "[gMiner]" + "\n" + "version=0.1.5"

	+ "\n" + "track1=/scratch/tracks/qual/sql/ribosome_genesis.sql"
	+ "\n" + "track1_name='Fake client track one'"
	+ "\n" + "track2=/scratch/tracks/qual/sql/ribosome_proteins.sql"
	+ "\n" + "track2_name='Fake client track two'"
	+ "\n" + "operation_type=desc_stat"
	+ "\n" + "characteristic=number_of_features"
	+ "\n" + "per_chromosome=True"
	+ "\n" + "compare_parents=False"
	+ "";

	// The url for posting
	public static final String address = "http://sugar.epfl.ch/gMiner/";

	public void sendPostRequest() {
		try {            
			// URL of web service
			URL url = new URL(address);
			// HTTP connection channel.
			HttpURLConnection   conn =  (HttpURLConnection) url.openConnection();
			// Let the run-time system (RTS) know that we want input.
			conn.setDoInput(true);
			// Let the RTS know that we want to do output.
			conn.setDoOutput(true);
			// Specify the method
			conn.setRequestMethod("POST");
			// No caching, we want the real thing.
			conn.setUseCaches(false);
			// Specify the content type and size.
			conn.setRequestProperty("Content-Type", "text/plain");
			conn.setRequestProperty("Content-Length",Integer.toString(content.length()));
			// Create output stream
			DataOutputStream output = new DataOutputStream(conn.getOutputStream());
			// Send POST output.
			output.writeBytes(content);
			output.flush();
			output.close();
			//output the response code
			System.out.println(conn.getResponseCode());
			//get the input stream
			DataInputStream inStream;
			try {
				inStream  = new DataInputStream(conn.getInputStream());
			} catch (IOException e) {
				inStream = new DataInputStream(conn.getErrorStream());
			} 
			//get the result as a String
			String buffer,result = "";
			InputStreamReader isr = new InputStreamReader(inStream);
			BufferedReader br = new BufferedReader(isr);
			while(null!=(buffer = br.readLine())){
				result+=buffer+"\n";
			}
			// Close the stream
			inStream.close();
			//output the result
			System.out.println(result);
		} catch (MalformedURLException ex) {
			ex.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	public static void main(String[] args) {
		new Client().sendPostRequest();
	}
}

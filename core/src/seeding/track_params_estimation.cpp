/** TRACCC library, part of the ACTS project (R&D line)
 *
 * (c) 2021-2023 CERN for the benefit of the ACTS project
 *
 * Mozilla Public License Version 2.0
 */

// Library include(s).
#include "traccc/seeding/track_params_estimation.hpp"

#include "traccc/edm/seed.hpp"
#include "traccc/seeding/track_params_estimation_helper.hpp"

#include <fstream>

namespace traccc {

track_params_estimation::track_params_estimation(vecmem::memory_resource& mr)
    : m_mr(mr) {}

track_params_estimation::output_type track_params_estimation::operator()(
    const spacepoint_collection_types::host& spacepoints,
    const seed_collection_types::host& seeds, const vector3& bfield,
    const std::array<traccc::scalar, traccc::e_bound_size>& stddev) const {

    const seed_collection_types::host::size_type num_seeds = seeds.size();
    output_type result(num_seeds, &m_mr.get());

    std::ofstream reconstructedTPs;
    reconstructedTPs.open("Plotting/TrackParams/reconstructedTPs.csv", std::ios_base::app);
    
    for (seed_collection_types::host::size_type i = 0; i < num_seeds; ++i) {
        bound_track_parameters track_params;
        track_params.set_vector(
            seed_to_bound_vector(spacepoints, seeds[i], bfield));

        // Set Covariance
        for (std::size_t j = 0; j < e_bound_size; ++j) {
            getter::element(track_params.covariance(), j, j) =
                stddev[j] * stddev[j];
        }

        // Get geometry ID for bottom spacepoint
        const auto& spB = spacepoints.at(seeds[i].spB_link);
        track_params.set_surface_link(spB.meas.surface_link);

        result[i] = track_params;

        //writes
        const auto& spM = spacepoints.at(seeds[i].spM_link);
        const auto& spT = spacepoints.at(seeds[i].spT_link);
        

        auto cov = track_params.covariance();

        for (auto dirComponent : track_params.dir())
        {
            reconstructedTPs << dirComponent << ", ";
        }        

        reconstructedTPs << track_params.phi() << ", "
                        << getter::element(cov, 2, 2) <<  ", "
                        << track_params.theta() << ", " 
                        << getter::element(cov, 3, 3) << ", "
                        << spB.x() << "," << spB.y() << "," << spB.z() << ","
                        << spM.x() << "," << spM.y() << "," << spM.z() << ","
                        << spT.x() << "," << spT.y() << "," << spT.z()
                        << std::endl;
                    
    }

    reconstructedTPs.close();


    return result;
}

}  // namespace traccc
